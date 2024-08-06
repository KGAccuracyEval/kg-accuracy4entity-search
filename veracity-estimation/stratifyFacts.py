import csv
import pandas as pd
import numpy as np


def stratifyCSRF(stratFeature, numStrata):
    """
    Perform stratification w/ Cumulative Square Root of Frequency (CSRF) based on stratification feature

    :param stratFeature: target stratification feature (must represent the entire population)
    :param numStrata: number of strata
    :return: feature indices divided into numStrata strata
    """

    # compute CSRF
    unique, counts = np.unique(stratFeature, return_counts=True)
    sqrt_counts = np.sqrt(counts)
    csrf = np.cumsum(sqrt_counts)
    csrf2unique = dict(zip(csrf, unique))

    # define boundaries for strata (intervals)
    strataSize = csrf[-1] / numStrata
    boundaries = [-1]
    boundaries += [strataSize * (i + 1) for i in range(numStrata - 1)]

    # sanity check
    assert len(boundaries) == numStrata

    # assign features to strata based on CSRF intervals
    strata = []
    for b in range(numStrata):
        if b == numStrata - 1:
            intervals = [csrf2unique[c] for c in csrf if c > boundaries[b]]
        else:
            intervals = [csrf2unique[c] for c in csrf if (c > boundaries[b]) and (c < boundaries[b + 1])]
        # store feature indices within stratum
        stratum = [i for i in range(len(stratFeature)) if stratFeature[i] in intervals]
        strata += [stratum]
    return strata


def main():
    df = pd.read_csv('../data/utility/factUtility.tsv', sep='\t')
    uStrata = stratifyCSRF(df['utility'].tolist(), 5)

    print('number of strata=5')
    print('mean and std utility per stratum')
    print('stratum 0: mean={} std={}'.format(np.mean(df.loc[uStrata[0], 'utility']), np.std(df.loc[uStrata[0], 'utility'])))
    print('stratum 1: mean={} std={}'.format(np.mean(df.loc[uStrata[1], 'utility']), np.std(df.loc[uStrata[1], 'utility'])))
    print('stratum 2: mean={} std={}'.format(np.mean(df.loc[uStrata[2], 'utility']), np.std(df.loc[uStrata[2], 'utility'])))
    print('stratum 3: mean={} std={}'.format(np.mean(df.loc[uStrata[3], 'utility']), np.std(df.loc[uStrata[3], 'utility'])))
    print('stratum 4: mean={} std={}'.format(np.mean(df.loc[uStrata[4], 'utility']), np.std(df.loc[uStrata[4], 'utility'])))

    # store strata as csv
    with open('../data/utility/stratifiedFacts.csv', 'w') as out:
        wr = csv.writer(out)
        wr.writerows(uStrata)


if __name__ == "__main__":
    main()
