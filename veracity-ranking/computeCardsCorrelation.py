import os
import json
import argparse
import itertools
import pandas as pd

from tqdm import tqdm
from scipy.stats import kendalltau
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument('--size', default=5, choices=[5, 10], help='Considered size for entity cards.')
parser.add_argument('--method', default='dynes_utility', choices=['dynes_utility', 'relin'], help='Target method.')
args = parser.parse_args()

formats = {'csv': ',', 'tsv': '\t'}


def break_ties(run):  # taken from https://github.com/irgroup/repro_eval/blob/master/repro_eval/util.py
    """
    Use this function to break score ties like it is implemented in trec_eval.
    Documents with the same score will be sorted in reverse alphabetical order.
    :param run: Run with score ties. Nested dictionary structure (cf. pytrec_eval)
    :return: Reordered run
    """
    for topic, ranking in run.items():
        docid_score_tuple = list(ranking.items())
        reordered_ranking = []
        for k, v in itertools.groupby(docid_score_tuple, lambda item: item[1]):
            reordered_ranking.extend(sorted(v, reverse=True))
        run[topic] = OrderedDict(reordered_ranking)
    return run


def _ktau_union(orig_run, rep_run, avoidQ, trim_thresh=10, pbar=False):  # taken and modified from https://github.com/irgroup/repro_eval/blob/master/repro_eval/measure/document_order.py
    """
    Helping function returning a generator to determine Kendall's tau Union (KTU) for all topics.

    @param orig_run: The original run.
    @param rep_run: The reproduced/replicated run.
    @param avoidQ: The set of queries to avoid considering
    @param trim_thresh: Threshold values for the number of documents to be compared.
    @param pbar: Boolean value indicating if progress bar should be printed.
    @return: Generator with KTU values.
    """

    generator = tqdm(rep_run.items()) if pbar else rep_run.items()

    for topic, docs in generator:
        if topic in avoidQ:
            continue
        orig_docs = list(orig_run.get(topic).keys())[:trim_thresh]
        rep_docs = list(rep_run.get(topic).keys())[:trim_thresh]
        union = list(sorted(set(orig_docs + rep_docs)))
        orig_idx = [union.index(doc) for doc in orig_docs]
        rep_idx = [union.index(doc) for doc in rep_docs]
        yield topic, round(kendalltau(orig_idx, rep_idx).correlation, 14)


def ktau_union(orig_run, rep_run, avoidQ, trim_thresh=10, pbar=False):  # taken and modified from https://github.com/irgroup/repro_eval/blob/master/repro_eval/measure/document_order.py
    """
    Determines the Kendall's tau Union (KTU) between the original and reproduced document orderings
    according to the following paper:
    Timo Breuer, Nicola Ferro, Norbert Fuhr, Maria Maistro, Tetsuya Sakai, Philipp Schaer, Ian Soboroff.
    How to Measure the Reproducibility of System-oriented IR Experiments.
    Proceedings of SIGIR, pages 349-358, 2020.

    @param orig_run: The original run.
    @param rep_run: The reproduced/replicated run.
    @param avoidQ: The set of queries to avoid considering
    @param trim_thresh: Threshold values for the number of documents to be compared.
    @param pbar: Boolean value indicating if progress bar should be printed.
    @return: Dictionary with KTU values that compare the document orderings of the original and reproduced runs.
    """

    return dict(_ktau_union(orig_run, rep_run, avoidQ, trim_thresh=trim_thresh, pbar=pbar))


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


def main():
    # read data
    df = readData('../data/corpus/fact_ranking_coll.tsv')
    # get id and (subj, pred, obj) facts from the collections
    facts = {}
    for row in df.iterrows():
        facts[row[0]] = {'subj': row[1]['en_id'], 'pred': row[1]['pred'], 'obj': row[1]['obj']}

    # read runs
    if args.method == 'dynes_utility':
        run = readRun('../data/runs/dynes_utility.run')
        rrun = readRun('../data/runs/vRankDynes.run')
    else:
        run = readRun('../data/runs/relin.run')
        rrun = readRun('../data/runs/vRankRELIN.run')

    # set the list of queries to avoid -- i.e., the queries w/ facts belonging to only one partition
    avoidQ = ['INEX_LD-2009111', 'INEX_LD-2010057', 'INEX_LD-20120122', 'INEX_LD-20120222', 'INEX_LD-2012319',
              'INEX_XER-129', 'INEX_XER-130', 'INEX_XER-81', 'QALD2_te-48', 'QALD2_te-82', 'QALD2_te-98',
              'SemSearch_ES-123', 'SemSearch_ES-66', 'SemSearch_ES-86', 'SemSearch_LS-31', 'SemSearch_LS-43']

    # prepare runs for Kendall's Tau Union (KTU) evaluation
    q2run = run.groupby('query')[['factID', 'score']].apply(lambda x: dict(x[['factID', 'score']].to_records(index=False)))
    q2rrun = rrun.groupby('query')[['factID', 'score']].apply(lambda x: dict(x[['factID', 'score']].to_records(index=False)))

    # compute KTU
    kTaus = ktau_union(q2run, q2rrun, avoidQ, trim_thresh=args.size)
    print(f'KTU={round(sum(kTaus.values())/len(kTaus), 2)} between {args.method} and its vRank at cutoff={args.size}')

    # restrict to queries w/ KTU lower than 0.8
    kTausFiltered = {q: score for q, score in kTaus.items() if score < 0.8}

    # create output dir
    os.makedirs('../data/cards/size='+str(args.size)+'/', exist_ok=True)

    # prepare entity cards for base method
    baseEntityCards = {}
    for q, qData in q2run.items():
        if q in kTausFiltered:
            runFactsFiltered = list(qData.keys())[:args.size]
            baseEntityCards[q] = []
            for factID in runFactsFiltered:
                factData = facts[factID]
                baseEntityCards[q].append((factData['subj'], factData['pred'], factData['obj']))

    with open('../data/cards/size='+str(args.size)+'/'+args.method+'.json', 'w') as out:
        json.dump(baseEntityCards, out)

    # prepare entity cards for re-ranked method
    vRankEntityCards = {}
    for q, qData in q2rrun.items():
        if q in kTausFiltered:
            runFactsFiltered = list(qData.keys())[:args.size]
            vRankEntityCards[q] = []
            for factID in runFactsFiltered:
                factData = facts[factID]
                vRankEntityCards[q].append((factData['subj'], factData['pred'], factData['obj']))

    if args.method == 'dynes_utility':
        with open('../data/cards/size='+str(args.size)+'/'+'vRankDynes.json', 'w') as out:
            json.dump(vRankEntityCards, out)
    else:
        with open('../data/cards/size='+str(args.size)+'/'+'vRankRELIN.json', 'w') as out:
            json.dump(vRankEntityCards, out)


if __name__ == "__main__":
    main()
