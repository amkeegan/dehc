import random
import sys
import time
import mods.database as md

# ----------------------------------------------------------------------

level = "WARNING" # Logging level
n = 5000          # Number of documents to insert
f = 20            # Number of fetches to make
q = 20            # Number of queries to make

# ----------------------------------------------------------------------

t0 = time.time()

# PREAMBLE

dehc = md.DEHCDatabase(config="db_auth.json", level=level, quickstart=True)
db = dehc.db

def rand_name():
    s = [random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(6)]
    return "".join(s)

def rand_id():
    s = [random.choice("0123456789abcdef") for _ in range(12)]
    return "".join(s)

def rand_ids():
    return [rand_id() for _ in range(random.randint(2,5))]

def rand_doc():
    return {"Name": rand_name(), "ID": rand_id(), "IDS": rand_ids(), "Notes": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed luctus commodo vehicula."}

docs = [rand_doc() for _ in range(n)]
t1 = time.time()

# INSERTING

ids = dehc.items_create(cat="person", docs=docs)
t2 = time.time()

# FETCHING ONE

for i in range(f):
    dehc.item_get(id=ids[i])
t3 = time.time()
for i in range(f):
    db.document_get(dbname="items", id=ids[i])
t4 = time.time()

# FETCHING ALL

for _ in range(f):
    dehc.items_list()
t5 = time.time()
for _ in range(f):
    db.documents_list(dbname="items", limit=n)
t6 = time.time()

# QUERY

dehc.items_query(cat="person", selector={'ID':{"$eq": docs[0]['ID']}}, fields=["name", "ID"], sort=[{"ID": "asc"}])
dehc.items_query(cat="person", selector={'IDS':{"$all": [docs[0]['IDS'][0]]}}, fields=["name", "IDS"], sort=[{"IDS": "asc"}])
dehc.items_query(cat="person", selector={'ID':{"$eq": docs[0]['ID']}}, fields=["name", "ID"], sort=[{"Name": "asc"}])
dehc.items_query(cat="person", selector={'IDS':{"$all": [docs[0]['IDS'][0]]}}, fields=["name", "IDS"], sort=[{"Name": "asc"}])

t7 = time.time()

for i in range(q):
    dehc.items_query(cat="person", selector={'ID':{"$eq": docs[i]['ID']}}, fields=["_id", "ID"], sort=[{"ID": "asc"}])
t8 = time.time()

for i in range(q):
    dehc.items_query(cat="person", selector={'ID':{"$eq": docs[i]['ID']}}, fields=["_id", "ID"], sort=[{"Name": "asc"}])
t9 = time.time()

for i in range(q):
    dehc.items_query(cat="person", selector={'IDS':{"$all": [docs[i]['IDS'][0]]}}, fields=["_id", "IDS"], sort=[{"IDS": "asc"}])
ta = time.time()

for i in range(q):
    dehc.items_query(cat="person", selector={'IDS':{"$all": [docs[i]['IDS'][0]]}}, fields=["_id", "IDS"], sort=[{"Name": "asc"}])
tb = time.time()

# RESULTS

places = 3  # Decimal places
print(f"Preamble: {round(t1-t0, places)} seconds")
print(f"Inserting {n} documents: {round(t2-t1, places)} seconds")
print(f"Fetching one document {f} times using DEHC: {round(t3-t2, places)} seconds")
print(f"Fetching one document {f} times using DB: {round(t4-t3, places)} seconds")
print(f"Fetching ALL {n} documents {f} times using DEHC: {round(t5-t4, places)} seconds")
print(f"Fetching ALL {n} documents {f} times using DB: {round(t6-t5, places)} seconds")
print(f"Querying ID (indexed by ID) in {n} documents {q} times: {round(t8-t7, places)} seconds")
print(f"Querying ID (indexed by Name) in {n} documents {q} times: {round(t9-t8, places)} seconds")
print(f"Querying list of IDs (indexed by IDS) in {n} documents {q} times: {round(ta-t9, places)} seconds")
print(f"Querying list of IDs (indexed by Name) in {n} documents {q} times: {round(tb-ta, places)} seconds")

input("Breakpoint. Press enter to delete database and finish.")

# POSTAMBLE

dehc.databases_delete()
sys.exit(0)