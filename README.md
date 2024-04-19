# Dissertation code base 


This repository contains the code used in my PhD dissertation titled _Information Dynamics in Low Countries' Chronicles (1500--1860). A Computational Approach_.

Author: Alie Lassche\
Version: 19 April 2024

## Project Organization

The organization of this repository is as follows:
```
├── corpus/
│   └── corpus_230811/                    <- corpus for chapter 3 and 5
│       ├── corpus_230811_annotated/      <- Topic Corpus
│       └── corpus_230811_full/           <- Full Corpus                
│
├── sources/               <- code for chapter 2 and 4
│   ├── scripts
│   └── data
│
└── topics/                <- code for chapter 3 and 5
    ├── application
    ├── scripts
    └── data 
```

## 1. Corpus

## 2. Sources

- analyse labels source mention with `sources/scripts/source_analysis_statistics.ipynb`
- analyse source categories with `sources/scripts/sources_categories_statistics.ipynb`
- count tokens and labels per chronicle with `sources/scripts/count_tokens_tags.ipynb`

## 3. Topics

### 3.1 Parsing XML files

```
cd topics/application
bash convert_from_xml.sh
```

### 3.2 Training a `Top2Vec` model

```
cd topics/application
python top2vec_training.py
```

In case of using month dates as well, don't forget to fill in the `xx` in the dates with `topics/scripts/clean_corrected_primitives.ipynb`

### 3.3 Prepare files for topical fluctuation

```
python topics/cossims_primitives_corrected_fast.py
```

Further steps:
- explore `Top2Vec` model with `topics/scripts/top2vec_exploring.ipynb`
- analyse `Top2Vec` model with `topics/scripts/top2vec_analysis.ipynb`
- explore primitives with `topics/scripts/primitives_analysis.ipynb`

### 3.4 Calculate topic distributions per chronicle

- `topics/topic_distribution_chronicles.ipynb`







