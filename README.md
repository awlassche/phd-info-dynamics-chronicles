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







