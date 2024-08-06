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
