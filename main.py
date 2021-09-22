'''The script that starts the main DEHC application.'''

import pprint
import random
import time
import sys

import apps.ems as ae
import mods.database as md
import mods.log as ml

# ----------------------------------------------------------------------------

level = "INFO"
logger = ml.get(name="Main", level=level)
logger.debug("Application has started.")

# ----------------------------------------------------------------------------

db = md.DEHCDatabase(config="db_auth.json", level=level, quickstart=True)

eid = db.item_create(cat="evacuation", doc={"Display Name":"DEHC Test"})
sids = db.items_create(cat="station", docs = [
    {"Display Name":"Ingest", "Index":0},
    {"Display Name":"Clean Hold", "Index":1}
])
fids = db.items_create(cat="family", docs = [
    {"Display Name":"Andrews Family"},
    {"Display Name":"Smith Family"},
    {"Display Name":"Williams Family"}
])
pids = db.items_create(cat="person", docs = [
    {"Display Name":"Alice Andrews", "Family Name":"Andrews", "Given Name(s)":"Alice", "Sex":"F", "Date Of Birth":"1984-12-02", "Passport Number":"M57976718", "Nationality":"AUS", "FlagA":1, "FlagB":0, "FlagC":1},
    {"Display Name":"Bob Andrews", "Family Name":"Andrews", "Given Name(s)":"Bob", "Sex":"M", "Date Of Birth":"1983-04-05", "Passport Number":"M37150257", "Nationality":"AUS", "FlagA":1, "FlagB":0},
    {"Display Name":"David Andrews", "Family Name":"Andrews", "Given Name(s)":"David", "Sex":"M", "Date Of Birth":"2004-05-08", "Passport Number":"M25452781", "Nationality":"AUS", "FlagA":1, "FlagC":1},
    {"Display Name":"Cecilia Smith", "Family Name":"Smith", "Given Name(s)":"Cecilia", "Sex":"F", "Date Of Birth":"2014-10-11", "Passport Number":"M16398048", "Nationality":"AUS", "FlagC":1},
    {"Display Name":"Frank Smith", "Family Name":"Smith", "Given Name(s)":"Frank", "Sex":"M", "Date Of Birth":"1992-08-14", "Passport Number":"M15252339", "Nationality":"AUS", "FlagA":0, "FlagB":1, "FlagC":1},
    {"Display Name":"Hazel Smith", "Family Name":"Smith", "Given Name(s)":"Hazel", "Sex":"F", "Date Of Birth":"1993-01-17", "Passport Number":"M70725449", "Nationality":"AUS", "FlagA":1, "FlagB":1},
    {"Display Name":"Emily Williams", "Family Name":"Williams", "Given Name(s)":"Emily", "Sex":"F", "Date Of Birth":"1970-03-20", "Passport Number":"M41117268", "Nationality":"AUS", "FlagB":0, "FlagC":1},
    {"Display Name":"George Williams", "Family Name":"Williams", "Given Name(s)":"George", "Sex":"M", "Date Of Birth":"1995-06-23", "Passport Number":"M70490680", "Nationality":"AUS", "FlagA":1, "FlagB":1, "FlagC":1},
    {"Display Name":"Isaac Clark", "Family Name":"Clark", "Given Name(s)":"Isaac", "Sex":"M", "Date Of Birth":"1989-02-26", "Passport Number":"M61132249", "Nationality":"NZL", "FlagB":1}
])

def fakename():
    name = ""
    for _ in range(12):
        c = random.choice("abcdefghijklmnopqrstuvwxyz")
        name += c
    return name

docs = []
for _ in range(10000):
    doc = {
        "Display Name": fakename(),
        "Family Name": fakename(),
        "Given Name(s)": fakename(),
        "Sex": fakename(),
        "Date Of Birth": fakename(),
        "Passport Number": fakename(),
        "Nationality": fakename(),
        "Home Address": fakename(),
        "Destination Address": fakename(),
        "Home Contact Number": fakename(),
        "Destination Contact Number": fakename(),
        "Guardian(s)": fakename(),
        "Requires Medical Attention?": fakename(),
        "Authority To Release Information?": fakename(),
        "Weight (KG)": fakename(),
        "Evacuee Searched?": fakename(),
        "Baggage Searched?": fakename(),
        "Documentation Completed?": fakename(),
        "Medical Completed?": fakename(),
        "Screening Completed?": fakename(),
        "Accommodation": fakename(),
        "Notes": fakename()
    }
    docs.append(doc)
db.items_create(cat="person", docs=docs)
q = docs[1000]["Display Name"]

#db.container_adds(container=fids[0], items=pids[:3])
#db.container_adds(container=fids[1], items=pids[3:6])
#db.container_adds(container=fids[2], items=pids[6:8])
#db.container_adds(container=sids[0], items=fids[:2]+pids[8:])
#db.container_adds(container=sids[1], items=fids[2:])
#db.container_adds(container=eid, items=sids)

# ----------------------------------------------------------------------------

#app = ae.EMS(db=db, level=level, autorun=True)
cat="person"
selector={"Display Name":{"$eq": q}}

input("Break")
t1 = time.time()
db.items_query(cat=cat, selector=selector)
t2 = time.time()
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
y = db.items_query(cat=cat, selector=selector)
t3 = time.time()

pprint.pprint(y)
print(t2-t1)
print(t3-t2)

# ----------------------------------------------------------------------------

logger.debug("Application is ending.")
sys.exit(0)
