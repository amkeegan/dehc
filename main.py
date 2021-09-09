'''The script that starts the main DEHC application.'''

import sys
from mods.database import DEHCDatabase

db = DEHCDatabase(config="db_auth.json", loud=True, quickstart=True)

x = db.item_create(cat="Person", doc={"Family Name": "Smith", "Given Name(s)": "Alice", "Sex": "F", "Date of Birth": "14/02/1990"})
y = db.item_create(cat="Person", doc={"Family Name": "Jones", "Given Name(s)": "Bob", "Sex": "M", "Date of Birth": "22/09/1985"})

input("Break point. Press enter.")

db.item_delete(id=x)
db.item_delete(id=y)

sys.exit(0)

