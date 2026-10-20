# kg-accuracy4entity-search

> **Research use only. Not a medical device.**
> This software was developed in the HEREDITARY project as a research prototype. It has not been assessed or certified under the EU Medical Device Regulation (EU) 2017/745. It must not be used to diagnose, treat, monitor or make any other decision about individual patients.

## 1. Overview

| Field | Value |
|---|---|
| Name | kg-accuracy4entity-search |
| Version | No tagged version (main branch) |
| Type | Software or library |
| Owner partner and contact | University of Padua (UNIPD), Stefano Marchesin, stefano.marchesin@unipd.it |
| License | MIT (see LICENSE file) |
| Repository and DOI | https://github.com/KGAccuracyEval/kg-accuracy4entity-search (no Zenodo DOI) |
| Release date | 6 August 2024 |
| Related task or deliverable | 4.1 |
| How to cite | S. Marchesin, G. Silvello and O. Alonso. Veracity Estimation for Entity-Oriented Search with Knowledge Graphs. CIKM 2024: 1649-1659. doi:10.1145/3627673.3679561 |

## 2. Intended use

**Primary intended use.** Code and derived data to estimate the veracity of DBpedia facts used in entity-oriented search and to measure its effect on fact ranking and entity-card generation. A utility model based on web popularity drives the stratification of facts; strata are annotated and their veracity estimated; entity-level veracity is used to re-rank facts (vRank) for the DynES and RELIN methods, with filtering and budget-constrained error correction.

**Intended users.** Researchers working on entity-oriented search and KG quality.

**Out-of-scope uses.** This release must not be used for
- clinical diagnosis, prognosis or treatment of individual patients;
- decisions about individuals, such as insurance, employment or access to care;
- re-identification of individuals or linkage with other data sources;
- populations, devices or data types not described in Section 3;

## 3. Data provenance

| Dataset | Source partner | Type (public, synthetic, pseudonymized, anonymized) | Population (size, age, sex, country, condition) | Ethics approval or access conditions |
|---|---|---|---|---|
| DynES fact-ranking collection (DBpedia 2015-10 facts, queries, utility judgments) and DynES/RELIN runs | External: Hasibi, Balog and Bratsberg, SIGIR 2017 | Public | Not applicable (KG triples; no human population) | Publicly available; downloaded by the user, not redistributed |
| Web result counts per entity (`data/utility`) | UNIPD, collected from Google Search for this study | Public | Not applicable | Released |
| Fact veracity annotations and entity-card preference judgments | UNIPD, produced for this study | Public (labels without annotator identifiers) | Not applicable | Released |

This repository and the released files contain no personal data, pseudonymized records, identifiers or pseudonymization keys.

## 6. Known limitations and risks

- **Generalizability.** Results refer to one KG snapshot (DBpedia 2015-10) and one test collection.
- **Known biases and confounders.** Utility derives from web popularity, which favors popular entities. Google result counts depend on the time, language and location of the request.
- **Failure modes.** `computeSearchCounts.py` parses Google result pages and fails when the page layout changes or no result count is shown; such entities must be handled manually. Entity-card preferences come from five assessors aggregated by majority voting.
- **Privacy risks.** No personal data and no trained model.

## 7. Responsible use and reporting

- **Terms of use.** MIT license. Research use only, as stated in the disclaimer above.
- **Contact for misuse or vulnerability reports.**

## 8. Acknowledgement

Funded by the European Union under grant agreement No 101137074 (HEREDITARY). Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Health and Digital Executive Agency (HaDEA). Neither the European Union nor the granting authority can be held responsible for them.
