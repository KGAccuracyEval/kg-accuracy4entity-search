import pandas as pd
import ir_measures as ireval

from ir_measures import *


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

    df = pd.read_csv(file, sep='\t', names=['query_id', 'entity', 'doc_id', 'rank', 'score', 'model'])
    return df


def readQrels(file):
    """
    read qrels and convert into dataframe
    :param file: input qrels
    :return: qrels as pandas dataframe
    """

    df = pd.read_csv(file, sep='\t', names=['query_id', 'entity', 'doc_id', 'relevance'])
    return df


# list of queries w/ all facts associated w/ the same veracity partition
query2remove = [
    'INEX_LD-2009111',
    'INEX_LD-2010057',
    'INEX_LD-20120122',
    'INEX_LD-20120222',
    'INEX_LD-2012319',
    'INEX_XER-129',
    'INEX_XER-130',
    'INEX_XER-81',
    'QALD2_te-48',
    'QALD2_te-82',
    'QALD2_te-98',
    'SemSearch_ES-123',
    'SemSearch_ES-66',
    'SemSearch_ES-86',
    'SemSearch_LS-31',
    'SemSearch_LS-43'
]


def main():
    # read runs
    dynes = readRun('../data/runs/dynes_utility.run')
    dynes['doc_id'] = dynes['doc_id'].astype(str)
    vRankDynes = readRun('../data/runs/vRankDynes.run')
    vRankDynes['doc_id'] = vRankDynes['doc_id'].astype(str)
    relin = readRun('../data/runs/relin.run')
    relin['doc_id'] = relin['doc_id'].astype(str)
    vRankRELIN = readRun('../data/runs/vRankRELIN.run')
    vRankRELIN['doc_id'] = vRankRELIN['doc_id'].astype(str)

    # read qrels
    qrels = readQrels('../data/corpus/qrels-utility.txt')
    qrels['doc_id'] = qrels['doc_id'].astype(str)
    # remove rows whose query is in query2remove -- i.e. queries w/ all facts associated w/ same veracity partition
    qrels = qrels[~qrels['query_id'].isin(query2remove)]

    # compute considered measures
    dynesScores = ireval.calc_aggregate([nDCG @ 5, nDCG @ 10], qrels, dynes)
    vRankDynesScores = ireval.calc_aggregate([nDCG @ 5, nDCG @ 10], qrels, vRankDynes)
    relinScores = ireval.calc_aggregate([nDCG @ 5, nDCG @ 10], qrels, relin)
    vRankRELINScores = ireval.calc_aggregate([nDCG @ 5, nDCG @ 10], qrels, vRankRELIN)

    # print performance
    print(f'DynES (orig): nDCG@5={round(dynesScores[nDCG @ 5], 2)}\tnDCG@10={round(dynesScores[nDCG @ 10], 2)}')
    print(f'DynES (vRank): nDCG@5={round(vRankDynesScores[nDCG @ 5], 2)}\tnDCG@10={round(vRankDynesScores[nDCG @ 10], 2)}')
    print(f'RELIN (orig): nDCG@5={round(relinScores[nDCG @ 5], 2)}\tnDCG@10={round(relinScores[nDCG @ 10], 2)}')
    print(f'RELIN (vRank): nDCG@5={round(vRankRELINScores[nDCG @ 5], 2)}\tnDCG@10={round(vRankRELINScores[nDCG @ 10], 2)}')


if __name__ == "__main__":
    main()
