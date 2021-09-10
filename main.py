'''The script that starts the main DEHC application.'''

import sys
from mods.database import DEHCDatabase

# ----------------------------------------------------------------------------

# Initialization

db = DEHCDatabase(config="db_auth.json", loud=True, quickstart=True)

pa = db.item_create(cat="person", doc={"Family Name": "Smith", "Given Name(s)": "Alice"})
pb = db.item_create(cat="person", doc={"Family Name": "Jones", "Given Name(s)": "Bob"})
pc = db.item_create(cat="person", doc={"Family Name": "Smith", "Given Name(s)": "Chris"})
pd = db.item_create(cat="person", doc={"Family Name": "Andrews", "Given Name(s)": "David"})
pe = db.item_create(cat="person", doc={"Family Name": "Andrews", "Given Name(s)": "Eric"})
pf = db.item_create(cat="person", doc={"Family Name": "Jones", "Given Name(s)": "Frank"})
pg = db.item_create(cat="person", doc={"Family Name": "Smith", "Given Name(s)": "George"})
ph = db.item_create(cat="person", doc={"Family Name": "Clark", "Given Name(s)": "Harry"})
fa = db.item_create(cat="family", doc={"Name": "The Smith Family"})
fb = db.item_create(cat="family", doc={"Name": "The Jones Family"})
fc = db.item_create(cat="family", doc={"Name": "The Andrews Family"})
sa = db.item_create(cat="station", doc={"Station": "Ingest"})
sb = db.item_create(cat="station", doc={"Station": "Clean Hold"})

db.container_adds(container=fa, items=[pa, pc, pg])
db.container_adds(container=fb, items=[pb, pf])
db.container_adds(container=fc, items=[pd, pe])
db.container_add(container=sa, item=fa)
db.container_add(container=sb, item=fb)
db.container_add(container=sb, item=fc)
db.container_add(container=sb, item=ph)
db.container_remove(container=sb, item=ph)
db.container_remove(container=sb, item=ph, lazy=True)
db.container_removes(container=sb, items=[fb, fc])
db.container_move(from_con=sa, to_con=sb, item=fa)
db.container_moves(from_con=sb, to_con=sa, items=[fa, ph], lazy=True)
print(db.container_exists(container=sa, item=ph))
print(db.containers_list())
print(db.containers_query())

db.databases_delete()
del db
sys.exit(0)
