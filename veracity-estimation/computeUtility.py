import pandas as pd

formats = {'csv': ',', 'tsv': '\t'}


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


def readSearchCounts(file):
    """
    read search counts and convert them into dictionary
    :param file: input file containing search counts
    :return: search counts as dict
    """

    with open(file, 'r') as f:
        searchCounts = f.readlines()
    searchCounts = [sC.strip().split('\t') for sC in searchCounts]
    searchCounts = {sC[0]: int(sC[1]) for sC in searchCounts}
    return searchCounts


def main():
    # read data
    df = readData('../data/corpus/fact_ranking_coll.tsv')
    # get id and (subj, pred, obj) facts from the collections
    _ids = df['id'].tolist()
    subj = df['en_id'].tolist()
    pred = df['pred'].tolist()
    obj = df['obj'].tolist()
    # read search counts
    search2count = readSearchCounts('../data/utility/searchCounts.txt')
    # iterate over facts and compute utility as utility(subject)+utility(object) -- here utility == popularity
    f2u = {}
    for s, p, o in zip(subj, pred, obj):
        f2u[(s, p, o)] = search2count[s]
        if o in search2count:
            f2u[(s, p, o)] += search2count[o]
    # normalize fact utility using min-max normalization
    minU = min(f2u.values())
    maxU = max(f2u.values())
    f2u = {f: (u-minU)/(maxU-minU) for f, u in f2u.items()}
    # associate each fact utility w/ orig id in collection
    f2id = {(s, p, o): _id for _id, s, p, o in zip(_ids, subj, pred, obj)}
    # store normalized fact utilities
    with open('../data/utility/factUtility.tsv', 'w') as out:
        out.write('id\tsubj\tpred\tobj\tutility\n')
        for f, u in f2u.items():
            out.write(str(f2id[f])+'\t'+f[0]+'\t'+f[1]+'\t'+f[2]+'\t'+str(u)+'\n')


if __name__ == "__main__":
    main()
