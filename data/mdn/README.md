git clone https://github.com/mdn/content/
rm db.db; python build_db.py ../../data/mdn/json/ ../../data/mdn/db.db
python ../../scripts/retriever/build_tfidf.py db.db .
python ../pipeline/interactive.py --retriever-model /home/andre/DrQA/data/mdn/db-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz --reader-model /tmp/drqa-models/20210325-6fbd5ef3.mdl --doc-db ~/DrQA/data/mdn/db.db
