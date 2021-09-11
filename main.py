'''The script that starts the main DEHC application.'''

import sys
from mods.database import DEHCDatabase

# ----------------------------------------------------------------------------

# Initialization

db = DEHCDatabase(config="db_auth.json", loud=False, quickstart=True)

pa = {"Family Name": "Smith", "Given Name(s)": "Alice", "Sex": "F", "Weight": "95", "Notes": "Likes walks on the beach."}
pb = {"Family Name": "Jones", "Given Name(s)": "Bob", "Sex": "M", "Weight": "100"}
pc = {"Family Name": "Smith", "Given Name(s)": "Curt", "Sex": "M", "Weight": "80", "Notes": "Afraid of heights."}
pd = {"Family Name": "Andrews", "Given Name(s)": "Diana", "Sex": "F", "Weight": "75"}
pe = {"Family Name": "Andrews", "Given Name(s)": "Eric", "Sex": "M", "Weight": "70", "Notes": "Chess world champion."}
pf = {"Family Name": "Jones", "Given Name(s)": "Franziska", "Sex": "F", "Weight": "85"}
pg = {"Family Name": "Smith", "Given Name(s)": "Gene", "Sex": "M", "Weight": "90", "Notes": "Can recite π to 100 places."}
ph = {"Family Name": "Clark", "Given Name(s)": "Harry", "Sex": "M", "Weight": "120"}
fa = {"Name": "The Smith Family", "Notes": "Won a free chocolate bar."}
fb = {"Name": "The Jones Family"}
fc = {"Name": "The Andrews Family", "Notes": "Seem kinda shady."}
sa = {"Station": "Processing", "Index": "1"}
sb = {"Station": "Clean Hold", "Index": "2"}

pa, pb, pc, pd, pe, pf, pg, ph = db.items_create(cat="person", docs=[pa, pb, pc, pd, pe, pf, pg, ph])
fa, fb, fc = db.items_create(cat="family", docs=[fa, fb, fc])
sa, sb = db.items_create(cat="station", docs=[sa, sb])

db.container_adds(container=fa, items=[pa, pc, pg])
db.container_adds(container=fb, items=[pb, pf])
db.container_adds(container=fc, items=[pd, pe])
db.container_add(container=sa, item=fa)
db.container_adds(container=sb, items=[fb, fc, ph])

input("Break. Press enter.")

db.databases_delete()
del db
sys.exit(0)
