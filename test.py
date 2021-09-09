'''Performance testing script.'''

import random
import sys
import time
from mods.database import Database

n = 2500 # Documents to insert
f = 50   # Documents to fetch
m = 50   # Queries to make

# Preamble
t1 = time.time()
db = Database(config="db_auth.json", loud=False)
if db.database_exists(dbname="testa"):
    db.database_delete(dbname="testa")
if db.database_exists(dbname="testb"):
    db.database_delete(dbname="testb")
db.database_create(dbname="testa")
db.database_create(dbname="testb")
t2 = time.time()
print(f"Preamble is {t2-t1} seconds.")

ids = db.id_create(n=n)
docs = [{"a": random.randint(1, n), "b": random.randint(1, n), "c": random.randint(1, n)} for _ in range(n)]

# Inserting data in BULK
t1 = time.time()
db.documents_create(dbname="testa", docs=docs, ids=ids)
t2 = time.time()
print(f"{n} inserts in BULK is {t2-t1} seconds.")

# Inserting data INDIVIDUALLY
t1 = time.time()
for i in range(n):
    db.document_create(dbname="testb", doc=docs[i], id=ids[i])
t2 = time.time()
print(f"{n} inserts INDIVIDUALLY is {t2-t1} seconds.")

f_ids = random.sample(ids, k=f)

# Fetching documents in BULK
t1 = time.time()
db.documents_get(dbname="testa", ids=f_ids)
t2 = time.time()
print(f"Fetching {f} in BULK is {t2-t1} seconds.")

# Fetching data INDIVIDUALLY
t1 = time.time()
for i in range(f):
    db.document_get(dbname="testb", id=f_ids[i])
t2 = time.time()
print(f"Fetching {f} INDIVIDUALLY is {t2-t1} seconds.")

# Creates and populates index
db.index_create(dbname="testa", name="test-index", fields=[{"a":"asc"}])
db.query(dbname="testa", selector={"a": {"$eq": 0}}, fields=["a"], sort=[{"a": "asc"}])
db.index_create(dbname="testb", name="test-index", fields=[{"_id":"asc"}])
db.query(dbname="testb", selector={"a": {"$eq": 0}}, fields=["_id"], sort=[{"_id": "asc"}])

# Queries Part 1
t1 = time.time()
for i in range(1, m+1):
    db.query(dbname="testa", selector={"a": {"$eq": i}}, fields=["a"], sort=[{"a": "asc"}])
t2 = time.time()
print(f"{m} queries on {n} documents, with good index, is {t2-t1} seconds")
t1 = time.time()
for i in range(1, m+1):
    db.query(dbname="testb", selector={"a": {"$eq": i}}, fields=["_id"], sort=[{"_id": "asc"}])
t2 = time.time()
print(f"{m} queries on {n} documents, with bad index, is {t2-t1} seconds")

arr = list(range(1, m+1))

# Queries Part 2
t1 = time.time()
db.query(dbname="testa", selector={"a": {"$in": arr}}, fields=["a"], sort=[{"a": "asc"}])
t2 = time.time()
print(f"1 query for {m} values in {n} documents, with good index, is {t2-t1} seconds")
t1 = time.time()
db.query(dbname="testb", selector={"a": {"$in": arr}}, fields=["_id"], sort=[{"_id": "asc"}])
t2 = time.time()
print(f"1 query for {m} values in {n} documents, with poor index, is {t2-t1} seconds")

sys.exit(0)

