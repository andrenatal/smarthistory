#!/bin/sh
source /Users/anatal/projects/stanford/DrQA/venv-drqa/bin/activate
export CLASSPATH=$CLASSPATH:/Users/anatal/projects/stanford/DrQA/data/corenlp/*
/Users/anatal/projects/stanford/DrQA/scripts/pipeline/nativemsg.py --retriever-model /Users/anatal/projects/stanford/DrQA/data/mdn/db-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz --reader-model /Users/anatal/projects/stanford/DrQA/data/mdn/single.mdl --doc-db /Users/anatal/projects/stanford/DrQA/data/mdn/db.db
