import random
import numpy as np
import pandas as pd

from tqdm import tqdm
from glob import glob


def readRun(file):
    """
    read run and convert into dataframe
    :param file: input run
    :return: run as pandas dataframe
    """

    fformat = file.split('.')[-1]
    if fformat != 'run':
        print('Format allowed is: run')
        raise Exception

    df = pd.read_csv(file, sep='\t', names=['query', 'entity', 'factID', 'rank', 'score', 'model'])
    return df


def fact2estimate(strataFile, annotPath):
    """
    associate each fact to the (estimated) partition accuracy
    :param strataFile: stored strata IDs
    :param annotPath: path to estimate stats
    :return: dict associating each fact ID with the corresponding partition estimate
    """

    # read strata file and store fact IDs within strata
    with open(strataFile, 'r') as f:
        strata = f.readlines()
    strata = [stratum.strip().split(',') for stratum in strata]
    strata = [[int(_id) for _id in stratum] for stratum in strata]

    # set vars
    strata2stats = {}
    fact2est = {}

    # read stats files
    statsPaths = glob(annotPath+'/partition*')
    # iterate over files and store stats info:
    for statPath in statsPaths:
        # get partition id
        _id = int(statPath.split('.tsv')[0][-1])
        df = pd.read_csv(statPath, sep='\t')
        strata2stats[_id] = df.values.tolist()

    # iterate over strata and associate to each fact ID the corresponding accuracy estimate (point estimate + CI)
    for i, facts in enumerate(strata):
        for fact in facts:
            if fact in fact2est:
                print('oh oh, this should not happen!')
                raise Exception
            fact2est[fact] = strata2stats[i]

    # return dict
    return fact2est


def main():
    # set seed
    np.random.seed(42)
    random.seed(42)

    # read run
    run = readRun('../data/runs/dynes_utility.run')
    # read fact accuracy estimates
    f2e = fact2estimate('../data/utility/stratifiedFacts.csv', '../data/stats/facts/')
    # create new column for run
    run['accEstimate'] = run['factID'].map(lambda x: f2e.get(x, [None])[0][0])

    # specify cutoffs to compute entity cards
    cutoffs = [5, 10]
    # count total number of queries
    totQueries = run.groupby('query').size().reset_index(name='row_count')
    totQueries = {cutoff: totQueries[totQueries['row_count'] >= cutoff].shape[0] for cutoff in cutoffs}
    # set percentages to compute budget
    percentage = [0.0, 0.01, 0.05, 0.1]
    # specify the different set of partitions to be filtered out
    accScoresList = [[0.6923076923076923], [0.6923076923076923, 0.7260726072607261, 0.7044025157232704], [0.6923076923076923, 0.7260726072607261, 0.7723880597014925, 0.7044025157232704]]

    for accScores in accScoresList:
        print(f'Accuracy score of filtered out partitions: {accScores}')

        # compute weights for popularity-based allocation strategy
        weights = [1 / ((pr+1) ** 2) for pr in range(len(accScores))]
        weights = [weight / sum(weights) for weight in weights]

        for perc in percentage:
            print('Budget allocated for error correction: {}%'.format(perc*100))

            # set the budget and decide how to allocate it across partitions
            budget = round(run.shape[0] * perc)

            # set up the budget allocation strategy
            popBudget = [round(budget * weight) for weight in weights]

            # allocate remaining budget across partitions
            for budgetStrat in [popBudget]:
                leftBudget = budget - sum(budgetStrat)
                k = 0
                while leftBudget != 0:
                    if leftBudget < 0:
                        budgetStrat[k] -= 1
                        leftBudget += 1
                    else:
                        budgetStrat[k] += 1
                        leftBudget -= 1

                    if k+1 == len(budgetStrat):
                        k = 0
                    else:
                        k += 1
            print(f'Amount of partition(s) covered by error correction when filtering is applied: {popBudget}')

            # prepare budget strategies
            budgetStrategies = [popBudget]
            strategyNames = ['Popularity-based allocation']

            for budgetXpartition, stratName in zip(budgetStrategies, strategyNames):  # iterate over budget allocation strategies
                assert budget == sum(budgetXpartition)  # sanity check
                print('Perform error correction with {}'.format(stratName))

                for cutoff in cutoffs:  # iterate over cutoff values
                    print('Entity card generated w/ {} facts'.format(cutoff))

                    # set var
                    qCounts = []

                    print('Removed {} partitions with veracity scores {}'.format(len(accScores), accScores))
                    for _ in tqdm(range(1000)):
                        cRun = run.copy(deep=True)
                        # iterate over partitions and sample triples w/ SRS to be annotated with 1
                        for j, acc in enumerate(accScores):
                            k = np.random.choice(run[run['accEstimate'] == acc].index, size=budgetXpartition[j], replace=False)
                            cRun.loc[k, 'accEstimate'] = 1.0
                        # remove rows with specific values in 'accEstimate'
                        fRun = cRun[~cRun['accEstimate'].isin(accScores)]

                        # group by 'query' and count the number of rows
                        queryCounts = fRun.groupby('query').size().reset_index(name='row_count')
                        queryCounts = queryCounts[queryCounts['row_count'] >= cutoff]
                        qCounts.append(queryCounts.shape[0])
                    print(f'{round(np.mean(qCounts), 1)} +\- {round(np.std(qCounts), 1)} entity cards generated out of {totQueries[cutoff]}')
                    print()
                print()
        print('\n')


if __name__ == "__main__":
    main()
