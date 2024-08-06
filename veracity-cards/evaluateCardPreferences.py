import pandas as pd

from glob import glob


def main():
    # get entity cards annotators' preferences
    annotPaths = glob('../data/annotations/cards/*.csv')

    dfs = []
    for path in annotPaths:  # store annotators' preferences as DataFrame
        dfs.append(pd.read_csv(path, delimiter=';'))

    annots = {}
    for df in dfs:  # iterate over annotator preferences to gather annotations
        for ix, row in df.iterrows():
            if row['query'] not in annots:  # new query -- set preferences dict
                annots[row['query']] = {'equal': 0, 'quality': 0, 'original': 0}

            # store annotations
            if row['Annotation'] == 'SAME':
                annots[row['query']]['equal'] += 1
            elif row['Annotation'] == row['QualityCard']:
                annots[row['query']]['quality'] += 1
            else:
                annots[row['query']]['original'] += 1

    scores = {'win': 0, 'loss': 0, 'tie': 0}
    for q, qAnnot in annots.items():  # iterate over counts and aggregate preferences via majority voting
        annots = [qAnnot['equal'], qAnnot['quality'], qAnnot['original']]

        maxA = max(annots)
        maxSize = len([v for v in annots if v == maxA])
        if maxSize > 1:  # store tie when there is no unique preference
            scores['tie'] += 1
        else:
            ix = annots.index(maxA)
            if ix == 0:
                scores['tie'] += 1
            elif ix == 1:
                scores['win'] += 1
            else:
                scores['loss'] += 1
    print('vRank summaries are')
    print(f'- deemed superior for {scores["win"]} ({round(scores["win"]/sum(scores.values())*100)}%) entity cards')
    print(f'- deemed inferior for {scores["loss"]} ({round(scores["loss"] / sum(scores.values())*100)}%) entity cards')
    print(f'- deemed equal for {scores["tie"]} ({round(scores["tie"] / sum(scores.values())*100)}%) entity cards')


if __name__ == "__main__":
    main()
