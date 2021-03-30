
# MDN DrQA

## This guide intends to describe the steps to train DrQA utilizing MDN data.

Setup DrQA
__________
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
__________
We trained the reader utilizing the Wikipedia and SQuAD datasets, so you can either train it yourself following the steps <a href="">here</a> (it takes around 2 hours on a RTX2080Ti), or download the <a href="https://github.com/andrenatal/DrQA/tree/mdn#trained-models-and-data">pre-trained models this way </a>. I suggest downloading/training but the sindle as the multitask models. Save the `.mdl` files into the `data/mdn` folder.

### Steps to train the retriever
__________
We utilized the data from the MDN github repo to train the document retriever, and you can follow the steps below to reproduce it. All the commands are meant to be ran in the repo's root folder.

- Pull MDN Data

        git clone https://github.com/mdn/content/ data/mdn/content

- Extract the content into json files

        python data/mdn/formatter.py

- Store the documents in the sqlite database

        python scripts/retriever/build_db.py data/mdn/json/ data/mdn/db.db

- Building the TF-IDF N-grams

        python scripts/retriever/build_tfidf.py data/mdn/db.db data/mdn/

After that you might have ~2695 entries in your model.

### Running the inference scripts
__________
-  The interactive reader
<small>
<!-- language: lang-none -->

        $ python scripts/reader/interactive.py --model data/mdn/multitask.mdl
        >>> text = "the internet explorer only html background sound element bgsound sets up a sound file to play in the background while the page is used use audio instead."
        >>> question = "What is the element used to add sound to a page?"
        >>> process(text, question)
        +------+-------+--------------------+
        | Rank |  Span |       Score        |
        +------+-------+--------------------+
        |  1   | audio | 0.8082995414733887 |
        +------+-------+--------------------+
</small>

- The interactive retriever
<small>
<!-- language: lang-none -->

        $ python scripts/retriever/interactive.py --model data/mdn/db-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz
        >>> process("How can I change the color of an element's border?", k=5)
        +------+-------------------------------------------------------------------------+-----------+
        | Rank |                                  Doc Id                                 | Doc Score |
        +------+-------------------------------------------------------------------------+-----------+
        |  1   | data/mdn/content/files/en-us/web/css/border-bottom-color/index.html-229 |   15.934  |
        |  2   |   data/mdn/content/files/en-us/web/css/border-top-color/index.html-182  |   15.934  |
        |  3   |  data/mdn/content/files/en-us/web/css/border-left-color/index.html-178  |   15.934  |
        |  4   |  data/mdn/content/files/en-us/web/css/border-right-color/index.html-192 |   15.934  |
        |  5   |    data/mdn/content/files/en-us/web/css/border-bottom/index.html-242    |   14.956  |
        +------+-------------------------------------------------------------------------+-----------+

</small>

- The interactive pipeline using the single model:
<small>
<!-- language: lang-none -->

        $ python scripts/pipeline/interactive.py --retriever-model data/mdn/db-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz --reader-model data/mdn/single.mdl --doc-db data/mdn/db.db
        >> process("What is the element used to create a hyperlink to webpages?", top_n=5, n_docs=5)
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

- The interactive pipeline using the multitalk model:
<small>
<!-- language: lang-none -->

        $ python scripts/pipeline/interactive.py --retriever-model data/mdn/db-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz --reader-model data/mdn/multitask.mdl --doc-db data/mdn/db.db
        >> process("What is the element used to create a hyperlink to webpages?", top_n=5, n_docs=5)
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

### Running the evaluators
__________
- Retriever
<small>
<!-- language: lang-none -->
        
        $ python scripts/retriever/eval.py data/mdn/eval.txt --model data/mdn/db-tfidf-ngram\=2-hash\=16777216-tokenizer\=simple.npz --doc-db data/mdn/db.db --n-docs 20        
        eval.txt
        Examples:                       20
        Matches in top 20:              16
        Match % in top 20:              80.00
        Total time:                     0.5038 (s)
</small>

- Pipeline (Reader + Retriever)
<small>
<!-- language: lang-none -->
        
        $ python scripts/pipeline/predict.py  --retriever-model data/mdn/db-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz --reader-model data/mdn/multitask.mdl --doc-db data/mdn/db.db data/mdn/eval.txt --n-docs 5 --top-n 5 --out-dir data/mdn/
        
        $ python data/mdn/eval_pipeline.py
        Total questions: 20
        Total matches: 8
        Total % matches: 40.0
</small>
