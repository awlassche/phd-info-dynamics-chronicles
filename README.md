# Dissertation code base 


This repository contains the code used in my PhD dissertation titled _Information Dynamics in Low Countries' Chronicles (1500--1860). A Computational Approach_.

Author: Alie Lassche\
Version: 8 April 2024

## Project Organization

The organization of this repository is as follows:
```
├── corpus/                <- trained top2vec model
│   ├── chronicles/         <- reusable
│   │   ├── entropies/          <- calculating indicator variables (incl. novelty)
│   │   ├── misc/               <- handling dates, etc.
│   │   ├── parser/             <- xml parsing, document segmentation
│   │   └── representation/     <- finding prototypes
│   └── ...
├── sources/          <- jupyter notebooks with exploratory analyses
│   └── ...
├── topics/             <- examples for the paper
│   └── ...
│
├── misc/
│
└── requirements.txt      <- install this
```

## 1. Corpus

## 2. Sources

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

In case of using month dates as well, don't forget to fill in the `xx` in the dates with `topics/clean_corrected_primitives.ipynb`

### 3.3 Prepare files for topical fluctuation

```
python topics/cossims_primitives_corrected_fast.py
```

Further steps:
- clean signal by removing false dates with `topics/edit_signal.ipynb` and `topics/signal.ipynb`
- explore `Top2Vec` model with `topics/top2vec_exploring.ipynb`
- analyse `Top2Vec` model with `topics/top2vec_analysis.ipynb`
- explore primitives with `topics/primitives_analysis.ipynb`

### 3.4 Calculate topic distributions per chronicle

- `topics/topic_distribution_chronicles.ipynb`







