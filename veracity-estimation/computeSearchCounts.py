import requests
import pandas as pd

from tqdm import tqdm
from bs4 import BeautifulSoup

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


def main():
    # read data
    df = readData('../data/corpus/fact_ranking_coll.tsv')
    # get subj and obj entities from the collection
    subj = set(df['en_id'].tolist())
    obj = df['obj'].tolist()
    obj = set([o for o in obj if o[:9] == '<dbpedia:'])
    # gather all entities together and remove unnecessary synthax
    ents = subj.union(obj)
    ents = [(' '.join(e[9:].split('_')), e) for e in ents]
    ents = [(e[0][:-1], e[1]) for e in ents]
    # read entities that have been parsed already
    with open('../data/utility/searchCounts.txt', 'r') as f:
        searchEnts = f.readlines()
    searchEnts = [e.split('\t') for e in searchEnts]
    searchEnts = {e[0]: e[1] for e in searchEnts}
    # perform (google) search based on entities
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
    with open('../utility/searchCounts.txt', 'a') as out:
        for e in tqdm(ents):
            if e[1] in searchEnts:
                continue
            url = "https://www.google.com/search?q="+e[0]
            result = requests.get(url, headers=headers)
            soup = BeautifulSoup(result.content, 'html.parser')
            result_stats_div = soup.find("div", {"id": "result-stats"})
            if result_stats_div:  # found num of results within html page
                countText = result_stats_div.find(text=True, recursive=False)  # give the full text
                count = ''.join([num for num in countText if num.isdigit()])  # clean and remove all chars that are not number
                out.write(e[1]+'\t'+count+'\n')
            else:  # not found -- (likely due to) low num of results
                print(e[0], e[1])  # show them and (for now) manually retrieve the total num


if __name__ == "__main__":
    main()
