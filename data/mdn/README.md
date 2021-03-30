
# MDN DrQA

## This guide intents to describe the steps to train DrQA utilizing MDN data.

### Setup DrQA

- Follow the installation steps described <a href="https://github.com/andrenatal/DrQA/tree/mdn#installing-drqa">here</a> to setup the DrQA virtualenv with all the pre-requirements. Make sure you are strictly using Pytorch 1.0 and Java 8. Pytorch 1.0 is compatible only with Cuda 10.0 (so make sure you have it installed if you are using GPUs) and Python 3.6.9. We are reproducing the setup steps below:

        pyenv install 3.6.9
        pyenv global 3.6.9
        python -m venv venv-drqa
        source venv-drqa/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        python setup.py develop
        pip install torch===1.0.0
        ./install_corenlp.sh
        export CLASSPATH=$CLASSPATH:data/corenlp/*

### Steps to train the reader

We trained the reader utilizing the Wikipedia and SQuAD datasets, so you can either train it yourself following the steps <a href="">here</a> (it takes around 2 hours on a RTX2080Ti), or download the <a href="https://github.com/andrenatal/DrQA/tree/mdn#trained-models-and-data">pre-trained models this way </a>. I suggest downloading/training but the sindle as the multitask models. Save the `.mdl` files into the `data/mdn` folder.

### Steps to train the retriever

We utilized the data from the MDN github repo to train the document retriever, and you can follow the steps below to reproduce it. All the commands are meant to be ran in the repo's root folder.

- Pull MDN Data

        git clone https://github.com/mdn/content/ data/mdn/content

- Extract the content into json files

        python data/mdn/formatter.py

- Store the documents in the sqlite database

        python scripts/retriever/build_db.py data/mdn/json/ data/mdn/db.db

- Building the TF-IDF N-grams

        python scripts/retriever/build_tfidf.py data/mdn/db.db data/mdn/

### Run the interactive reader

### Run the interactive retriever

### Run the complete interactive pipeline

- Utilizing the single model:

        $ python scripts/pipeline/interactive.py --retriever-model data/mdn/db-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz --reader-model data/mdn/single.mdl --doc-db data/mdn/db.db
        >> process("What is the element used to create a hyperlink to webpages?", top_n=5, n_docs=5)
Top Predictions:
<small>
<!-- language: lang-none -->
        +------+--------------------------------------------------------------------------+-----------------------------------------------------------------------------+--------------+-----------+
        | Rank |                                  Answer                                  |                                     Doc                                     | Answer Score | Doc Score |
        +------+--------------------------------------------------------------------------+-----------------------------------------------------------------------------+--------------+-----------+
        |  1   |                           interactive controls                           |      data/mdn/content/files/en-us/web/html/element/input/index.html-24      |    184.48    |   5.3796  |
        |  2   | href attribute, creates a hyperlink to web pages, files, email addresses |        data/mdn/content/files/en-us/web/html/element/a/index.html-77        |    85.179    |   13.761  |
        |  3   |                                    b                                     |        data/mdn/content/files/en-us/web/html/element/b/index.html-116       |    19.948    |   5.3796  |
        |  4   |                                   css                                    |      data/mdn/content/files/en-us/web/html/applying_color/index.html-3      |    1.6498    |   5.3796  |
        |  5   |                           fallback descriptor                            | data/mdn/content/files/en-us/web/css/@counter-style/fallback/index.html-307 |   0.032813   |   5.3796  |
        +------+--------------------------------------------------------------------------+-----------------------------------------------------------------------------+--------------+-----------+
</small>

- Utilizing the multitalk model:

        $ python scripts/pipeline/interactive.py --retriever-model data/mdn/db-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz --reader-model data/mdn/multitask.mdl --doc-db data/mdn/db.db
        >> process("What is the element used to create a hyperlink to webpages?", top_n=5, n_docs=5)
Top Predictions:
<small>
<!-- language: lang-none -->
        +------+--------------------------------------------------------------------------+-----------------------------------------------------------------------------+--------------+-----------+
        | Rank |                                  Answer                                  |                                     Doc                                     | Answer Score | Doc Score |
        +------+--------------------------------------------------------------------------+-----------------------------------------------------------------------------+--------------+-----------+
        |  1   |             href attribute, creates a hyperlink to web pages             |        data/mdn/content/files/en-us/web/html/element/a/index.html-77        |    146.57    |   13.761  |
        |  2   |        html input element is used to create interactive controls         |      data/mdn/content/files/en-us/web/html/element/input/index.html-24      |    32.272    |   5.3796  |
        |  3   |                    html bring attention to element b                     |        data/mdn/content/files/en-us/web/html/element/b/index.html-116       |    28.334    |   5.3796  |
        |  4   | html elements to create just the look you want. this article is a primer |      data/mdn/content/files/en-us/web/html/applying_color/index.html-3      |   0.75929    |   5.3796  |
        |  5   |                                  marker                                  | data/mdn/content/files/en-us/web/css/@counter-style/fallback/index.html-307 |   0.20582    |   5.3796  |
        +------+--------------------------------------------------------------------------+-----------------------------------------------------------------------------+--------------+-----------+
</small>

### Run the retriever evaluator

        python scripts/retriever/eval.py