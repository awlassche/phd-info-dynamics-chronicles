# Dissertation code base 


This repository contains the code used in my PhD dissertation titled _Information Dynamics in Low Countries' Chronicles (1500--1860). A Computational Approach_.

Author: Alie Lassche\
Version: 8 April 2024

## Project Organization

The organization of this repository is as follows:
```
├── chronicling_corpus/                <- trained top2vec model
│   ├── chronicles/         <- reusable
│   │   ├── entropies/          <- calculating indicator variables (incl. novelty)
│   │   ├── misc/               <- handling dates, etc.
│   │   ├── parser/             <- xml parsing, document segmentation
│   │   └── representation/     <- finding prototypes
│   └── ...
├── chronicling_sources/          <- jupyter notebooks with exploratory analyses
│   └── ...
├── chronicling_topics/             <- examples for the paper
│   └── ...
│
├── src/                <- analysis scripts
│   ├── chronicles/         <- reusable
│   │   ├── entropies/          <- calculating indicator variables (incl. novelty)
│   │   ├── misc/               <- handling dates, etc.
│   │   ├── parser/             <- xml parsing, document segmentation
│   │   └── representation/     <- finding prototypes
│   │
|   └── application/         <- ad hoc scripts
│       ├── config/             <- yaml files specifying parameters for experiments
│       ├── topics/             <- training the top2vec model
│       ├── visualization/      <- some more complicated publication plots (the less complicated are in notebooks/)
│       ├── convert_from_xml.sh <- shell script for running XML parsing
│       └── novelty_signal.py   <- pipeline for fitting the novelty signal
│
└── requirements.txt      <- install this
```







