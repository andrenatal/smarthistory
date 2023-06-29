#!/usr/bin/env python
# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
"""Interactive interface to full DrQA pipeline."""

import argparse
import logging
import sys
import json
import struct
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

conn = sqlite3.connect('./tests/history.db')
cursor = conn.cursor()
qa_model = pipeline("question-answering")
sentencetransformer = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
client = QdrantClient(path="./")
client.recreate_collection(
    collection_name="smarthistory",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

def indexa(html, url,title, _idx):
    bs = BeautifulSoup(html, "html.parser")
    text = bs.find('body').get_text()
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
                payload={"url" : url, "title": title}
            )
        ]
    )

def askquestion(question, items):
    try:
        log("processing question: " + question)
        query_vector = sentencetransformer.encode(question).tolist()
        log("query_vector ")

        hits = client.search(
            collection_name="smarthistory",
            query_vector=query_vector,
            limit=int(items),
            with_vectors=True
        )

        log("hits ")

        sql_search = "select data from history where idx = ?"
        responses = []
        for hit in hits:
            #print(hit.score, hit.payload)
            cursor.execute(sql_search, [hit.id])
            rows = cursor.fetchall()
            answer = qa_model(question = [question] , context = rows[0][0])
            responses.append({
                "hitscore": hit.score,
                "hitpayload": hit.payload,
                "answer": answer
            })
            log(f"hit.score: {hit.score} hit.payload {hit.payload} answer {answer}")
        return responses
    except Exception as err:
        log(f"Unexpected {err=}, {type(err)=}")

def process(question, candidates=None, top_n=1, n_docs=5):
#        sendMessage(encodeMessage(p['span'] + "|" + p['doc_id'] + "|" + '%.5g' % p['span_score'] + "|" '%.5g' % p['doc_score'] + "|" + output))
    sendMessage(encodeMessage("processed"))

# Python 3.x version
# Read a message from stdin and decode it.
def getMessage():
    try:
        rawLength = sys.stdin.buffer.read(4)
        if len(rawLength) == 0:
            sys.exit(0)
        messageLength = struct.unpack('@I', rawLength)[0]
        message = sys.stdin.buffer.read(messageLength).decode('utf-8')
        return json.loads(message)
    except Exception:
        log(Exception)

# Encode a message for transmission,
# given its content.
def encodeMessage(messageContent):
    encodedContent = json.dumps(messageContent).encode('utf-8')
    encodedLength = struct.pack('@I', len(encodedContent))
    return {'length': encodedLength, 'content': encodedContent}

# Send an encoded message to stdout
def sendMessage(encodedMessage):
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.buffer.write(encodedMessage['content'])
    sys.stdout.buffer.flush()

def log(dados):
    with open('/Users/anatal/projects/mozilla/smarthistory/scripts/pipeline/log.txt', 'a') as f:
        f.writelines(dados)
        f.writelines('\n')

while True:
    idx_counter = 0
    receivedMessage = getMessage()
    log(receivedMessage["command"])
    if receivedMessage["command"] == "index":
        log("indexa:")
        log(receivedMessage["url"])
        log(receivedMessage["body"])
        sendMessage(encodeMessage("{\"command\": \"indexing\"}"))
        indexa(receivedMessage["body"],receivedMessage["url"], receivedMessage["title"], idx_counter+1)
        sendMessage(encodeMessage("{\"command\": \"indexed\"}"))
    elif receivedMessage["command"] == "question":
        log("question")
        sendMessage(encodeMessage("{\"command\": \"processing\"}"))
        responselist = askquestion(receivedMessage["question"], receivedMessage["items"])
        response = {
            "command": "processed",
            "responses": responselist
        }
        json_str = json.dumps(response)
        log("return:" + json_str)
        sendMessage(encodeMessage(json_str))