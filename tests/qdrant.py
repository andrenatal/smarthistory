from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import numpy as np
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer, util
from bs4 import BeautifulSoup
import hashlib
import requests
import sqlite3
from transformers import pipeline

question = "What's the browser built by Mozilla?"

conn = sqlite3.connect('./tests/history.db')
cursor = conn.cursor()

qa_model = pipeline("question-answering")
sentencetransformer = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
client = QdrantClient(path="./")

client.recreate_collection(
    collection_name="smarthistory",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

def index(url, _idx):
    response = requests.get(url)
    bs = BeautifulSoup(response.text, "html.parser")
    text = bs.find('body').get_text()
    title = bs.find('title').get_text()
    embeddings = sentencetransformer.encode(text)
    point_id = hashlib.md5(f"{url}-{_idx}".encode()).hexdigest()
    sql = "INSERT INTO history VALUES (?,?,?)"
    records = [point_id, text, title]
    cursor.execute(sql, records)
    conn.commit()

    client.upsert(
        collection_name="smarthistory",
        points=[
            PointStruct(
                id=point_id,
                vector=embeddings.tolist(),
                payload={"url" : url, "title": title }
            )
        ]
    )

index("https://www.mozilla.org/en-US/firefox/" ,1)
index("https://www.google.com/chrome/", 2)
index("https://www.apple.com/safari/", 4)
index("https://www.microsoft.com/en-us/edge", 3)

query_vector = sentencetransformer.encode(question).tolist()

hits = client.search(
    collection_name="smarthistory",
    query_vector=query_vector,
    limit=1,
    with_vectors=True
)

sql_search = "select data from history where idx = ?"
for hit in hits:
    print(hit.score, hit.payload)
    cursor.execute(sql_search, [hit.id])
    rows = cursor.fetchall()
    answer = qa_model(question = [question] , context = rows[0][0])

conn.close()

