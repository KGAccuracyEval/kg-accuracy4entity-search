# Veracity Estimation for Entity-Oriented Search with Knowledge Graphs
We discuss the potential costs that emerge from using a Knowledge Graph (KG) in entity-oriented search without considering its data veracity. We argue for the need for KG veracity analysis to gain insights and propose a scalable assessment framework. Previous assessments focused on relevance, assuming correct KGs, and overlooking the potential risks of misinformation. Our approach strategically allocates annotation resources, optimizing utility and revealing the significant impact of veracity on entity search and card generation. Contributions include a fresh perspective on entity-oriented search extending beyond the conventional focus on relevance, a scalable assessment framework, exploratory experiments highlighting the impact of veracity on ranking and user experience, as well as outlining associated challenges and opportunities.

## Contents

This repository contains the source code to estimate and use KG veracity for entity-oriented search. <br>
Instructions on installation, acquisition and preparation of the data used for the experiments, and deployment of exploratory experiments are reported below.

## Installation 

Clone this repository

```bash
git clone https://github.com/KGAccuracyEval/kg-accuracy4entity-search.git
```

Install Python 3.10 (preferably in a virtual environment). <br>
Install all the requirements:

```bash
pip install -r requirements.txt
```

## Test Collection 

We consider the collection proposed by [Hasibi et al.](http://hasibi.com/files/sigir2017-dynes.pdf) for dynamic entity summarization. The collection adopts DBpedia (version 2015-10) as the underlying KG. For the experiments, the following files must be downloaded and moved to ```./data/corpus/```: <br>
- [fact_ranking_coll.tsv](https://github.com/iai-group/DynamicEntitySummarization-DynES/blob/master/data/fact_ranking_coll.tsv)
- [queries.txt](https://github.com/iai-group/DynamicEntitySummarization-DynES/blob/master/data/queries.txt)
- [qrels-utility.txt](https://github.com/iai-group/DynamicEntitySummarization-DynES/blob/master/data/qrels-utility.txt)

Together with the corpus, we also require [dynes_utility.run](https://github.com/iai-group/DynamicEntitySummarization-DynES/blob/master/runs/dynes_utility.run) and [relin.run](https://github.com/iai-group/DynamicEntitySummarization-DynES/blob/master/runs/relin.run) runs, which must be downloaded and moved to ```./data/runs/```.

## Experiments

### Veracity Estimation

For this set of experiments, move to ```./veracity-estimation/``` folder. <br>
The veracity estimation process is divided in the following steps:
1) <b>Utility Model:</b>
   - compute facts popularity on the Web using ```computeSearchCounts.py```, the outcomes are stored in [./data/utility/searchCounts.txt](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/blob/main/data/utility/searchCounts.txt).
   - compute facts utility using ```computeUtility.py```, the outcomes are stored in [./data/utility/factUtility.tsv](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/blob/main/data/utility/factUtility.tsv).

2) <b>Graph Partitioning:</b>
   - partition the KG based on facts utility via ```stratifyFacts.py```, the resulting strata are stored in [./data/utility/stratifiedFacts.csv](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/blob/main/data/utility/stratifiedFacts.csv).
  
3) <b>Partition Veracity Estimation:</b>
   - relying on ```samplingTechniques.py```, interact with ```estimateStrataAccuracy.ipynb``` to manually annotate facts correctness and estimate veracity.
   - once the estimation process ends, annotations are stored in [./data/annotations/facts/](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/tree/main/data/annotations/facts) and veracity estimates in [./data/stats/facts/](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/tree/main/data/stats/facts).
  
4) <b>Entity Veracity Estimation:</b>
   - compute entity-level veracity via ```computeEntityVeracity.py```, the veracity estimates are stored in [./data/stats/entities/entityVeracity.tsv](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/blob/main/data/stats/entities/entityVeracity.tsv).

### Fact Ranking

For this set of experiments, move to ```./veracity-ranking/``` folder. <br>
- run ```python reRank.py --method dynes_utility``` to perform the veracity-enhanced re-ranking strategy on DynES, which is stored in [./data/runs/vRankDynes.run](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/blob/main/data/runs/vRankDynes.run).
- run ```python reRank.py --method relin``` to perform the veracity-enhanced re-ranking strategy on RELIN, which is stored in [./data/runs/vRankRELIN.run](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/blob/main/data/runs/vRankRELIN.run).
- run ```python evaluateRuns.py``` to evaluate performance of baseline and <i>v</i>Rank methods for nDCG@5 and nDCG@10.
- compute Kendall's &tau; Union (KTU) correlations between baseline and <i>v</i>Rank methods at cutoffs 5 and 10 using ```computeCardsCorrelation.py```, the cutoff value can be set via ```--size``` and the considered method via ```--method```. Allowed sizes are ```5``` or ```10```, while allowed methods are ```dynes_utility``` or ```relin```.
- besides reporting KTU correlations, the script also stores entity cards at desired cutoffs for the considered methods when KTU < 0.8 -- e.g., the entity cards of size 5 for original and <i>v</i>Rank DynES methods are stored in [./data/cards/size=5/](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/tree/main/data/cards/size%3D5).

### Entity Cards

For this set of experiments, move to ```./veracity-cards/``` folder. <br>
- relying on the original and <i>v</i>Rank DynES entity cards of size 5 stored in [./data/cards/size=5/](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/tree/main/data/cards/size%3D5), interact with ```evaluateEntityCards.ipynb``` to manually annotate cards for preference.
- once the annotation process ends, preferences are stored in [./data/annotations/cards/](https://github.com/KGAccuracyEval/kg-accuracy4entity-search/tree/main/data/annotations/cards).
- run ```python evaluateCardPreferences.py``` to evaluate card preferences, obtained by aggregating (five) user preferences via majority voting.

### Budget-Constrained Error Correction

For this set of experiments, move to ```./budget-correction/``` folder. <br>


## Acknowledgments
The work is partially supported by the HEREDITARY project, as part of the EU Horizon Europe research and innovation programme under Grant Agreement No GA 101137074.

## Reference
If you use or extend our work, please cite the following:

```
@inproceedings{marchesin_etal-cikm2024,
  author = {S. Marchesin and G. Silvello and O. Alonso},
  title = {Veracity Estimation for Entity-Oriented Search with Knowledge Graphs},
  booktitle = {Proceedings of the 33rd ACM International Conference on Information and Knowledge Management (CIKM '24), October 21--25, 2024, Boise, ID, USA},
  publisher = {{ACM}},
  year = {2024},
  doi = {10.1145/3627673.3679561}
}
```



