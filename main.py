'''The script that starts the main DEHC application.'''

import sys
from mods.database import DEHCDatabase

# ----------------------------------------------------------------------------

# Initialization

db = DEHCDatabase(config="db_auth.json", loud=True, quickstart=True)


# Testing inserts

x = {"Family Name": "Smith", "Given Name(s)": "Alice", "Sex": "F", "Date of Birth": "14/02/1990"}
y = {"Family Name": "Jones", "Given Name(s)": "Bob", "Sex": "M", "Date of Birth": "22/09/1985"}
z = {"Name": "The Test Family"}

x, y = db.items_create(cat="person", docs=[x, y])
z = db.item_create(cat="family", doc=z)
print(x, "\n", y, "\n", z, sep="")


# Testing schema commands

a = db.schema_fields(cat="person")
b = db.schema_fields(id=x)
c = db.schema_keys(cat="person")
d = db.schema_keys(id=y)
print(a, "\n", b, "\n", c, "\n", d, sep="")


# Testing item existance

a = db.item_exists(id=x)
b = db.item_exists(id=y)
c = db.item_exists(id=z)
d = db.item_exists(id="fake")
print(a, "\n", b, "\n", c, "\n", d, sep="")


# Testing item listing

a = db.items_list()
b = db.items_list(cat="person", fields=["_id", "Family Name", "Given Name(s)"])
c = db.items_list(cat="family", fields=["_id", "Name"])
print(a, "\n", b, "\n", c, sep="")


# Testing item edits

a = db.items_edit(ids=[x, y, "fake"], data=[{"Notes":"Clever."}, {"Notes":"Handsome."}], lazy=True)
b = db.item_edit(id=z, data={"Notes":"Testy."})
c = db.item_edit(id="fake", data={}, lazy=True)
print(a, "\n", b, "\n", c, sep="")


# Testing item fetching

a = db.items_get(ids=[x, y, "fake"], fields=["_id", "Family Name", "Given Name(s)"], lazy=True)
b = db.item_get(id=z)
c = db.item_get(id="fake", fields=["_id"], lazy=True)
print(a, "\n", b, "\n", c, sep="")


# Testing item queries

a = db.items_query(cat="person", selector={'Family Name': {"$gt":"c"}}, fields=["_id", "Family Name", "Given Name"], sort=[{"_id": "asc"}])
b = db.items_query(selector={'Notes': {"$ne":"Handsome."}})
c = db.items_query(cat="person", sort=[{"_id": "desc"}])
d = db.items_query(cat="fake")
e = db.items_query()
print(a, "\n", b, "\n", c, "\n", d, "\n", e, sep="")


# Testing item deletion

input("Break. Press enter to continue.")

a = db.items_delete(ids=[x, y, "fake"], lazy=True)
b = db.item_delete(id=z)
c = db.item_delete(id="fake", lazy=True)
print(a, "\n", b, "\n", c, sep="")


# Clean up

db.databases_delete()
del db
sys.exit(0)
