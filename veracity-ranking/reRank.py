import argparse
import pandas as pd

from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument('--method', default='dynes_utility', choices=['dynes_utility', 'relin'], help='Target method.')
args = parser.parse_args()


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
    statsPaths = glob(annotPath+'partition*')
    # iterate over files and store stats info:
    for statPath in statsPaths:
        # get partition id
        _id = int(statPath.split('.tsv')[0][-1])
        df = pd.read_csv(statPath, sep='\t')
        strata2stats[_id] = df.values.tolist()

    # iterate over strata and associate to each fact ID the corresponding accuracy estimate (point estimate + CI)
    for i, facts in enumerate(strata):
        for fact in facts:
            fact2est[fact] = strata2stats[i]

    # return dict
    return fact2est


def main():
    # read run
    run = readRun('../data/runs/'+args.method+'.run')
    # read fact accuracy estimates
    f2e = fact2estimate('../data/utility/stratifiedFacts.csv', '../data/stats/facts/')
    # create new column for run
    run['accEstimate'] = run['factID'].map(lambda x: f2e.get(x, [None])[0][0])

    # perform min-max normalization over score
    run['score'] = run.groupby('query')['score'].transform(lambda x: (x - x.min()) / (x.max() - x.min()))
    # sum scores w/ accuracy estimates to perform re-ranking
    run['score'] += run['accEstimate']

    # re-rank based on the updated score
    run = run.groupby('query').apply(lambda group: group.sort_values(by='score', ascending=False))
    # reset the index after sorting
    run.reset_index(drop=True, inplace=True)
    # reset the ranking order
    run.loc[:, 'rank'] = run.groupby('query').cumcount() + 1

    # drop accEstimate column
    run = run.drop(['accEstimate'], axis=1)

    # store re-ranked run
    if args.method == "dynes_utility":
        run['model'] = 'vRankDynes'
        run.to_csv('../data/runs/vRankDynes.run', sep='\t', header=False, index=False)
    else:
        run['model'] = 'vRankRELIN'
        run.to_csv('../data/runs/vRankRELIN.run', sep='\t', header=False, index=False)


if __name__ == "__main__":
    main()
