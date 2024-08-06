import os
import numpy as np
import pandas as pd

from glob import glob
from scipy import stats


formats = {'csv': ',', 'tsv': '\t'}


class Estimator(object):
    """
    This class represents the Estimator used to perform entity accuracy estimation.
    """

    def __init__(self, alpha=0.05):
        """
        Initialize the sampler and set confidence level plus Normal critical value z with right-tail probability αlpha/2

        :param alpha: the user defined confidence level
        """

        # confidence level
        self.alpha = alpha
        self.z = stats.norm.isf(self.alpha/2)

    def estimate(self, sample):
        """
        Estimate the KG accuracy based on sample

        :param sample: input sample (i.e., set of triples) used for estimation
        :return: KG accuracy estimate
        """

        return sum(sample)/len(sample)

    def computeVar(self, sample):
        """
        Compute the sample variance

        :param sample: input sample (i.e., set of triples) used for estimation
        :return: sample variance
        """

        ae = self.estimate(sample)

        # count number of clusters in sample
        n = len(sample)

        if n*(n-1) != 0:  # compute variance
            var = (1/(n*(n-1))) * sum([(t - ae) ** 2 for t in sample])
        else:  # set variance to inf
            var = np.inf
        return var

    def computeMoE(self, sample):
        """
        Compute the Margin of Error (MoE) based on the sample and the Normal critical value z with right-tail probability α/2

        :param sample: input sample (i.e., set of triples) used for estimation
        :return: the MoE value
        """

        # compute sample variance
        var = self.computeVar(sample)
        # compute the margin of error (i.e., z * sqrt(var))
        moe = self.z * (var ** 0.5)
        return moe


def readData(file):
    """
    read dataset and convert into dataframe
    :param file: input file containing collection
    :return: dataset as pandas dataframe
    """

    fformat = file.split('.')[-1]
    if fformat not in formats:
        print('Formats allowed are: {}'.format(formats.keys()))
        raise Exception

    df = pd.read_csv(file, sep=formats[fformat])
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
    # set estimator
    estimator = Estimator()

    # read data
    df = readData('../data/corpus/fact_ranking_coll.tsv')
    # read fact accuracy estimates
    f2e = fact2estimate('../data/utility/stratifiedFacts.csv', '../data/stats/facts/')

    # create new columns for data
    df['accEstimate'] = df['id'].map(lambda x: f2e.get(x, [None])[0][0])

    # group by (query) entity
    dfQuery = df.groupby('en_id')

    # create output dir
    os.makedirs('../data/stats/entities/', exist_ok=True)

    with open('../data/stats/entities/entityVeracity.tsv', 'w') as out:  # store entity veracity
        out.write('entity\tmean\tmoe\n')
        # iterate over each query
        for query, triples in dfQuery:
            mean = estimator.estimate(triples['accEstimate'])
            moe = estimator.computeMoE(triples['accEstimate'])
            # store compute data
            out.write('{}\t{}\t{}\n'.format(query, mean, moe))


if __name__ == "__main__":
    main()
