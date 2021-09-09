'''The script that starts the main DEHC application.'''

import sys
from mods.database import DEHCDatabase

db = DEHCDatabase(config="database.json", loud=True)
db.create_databases()
db.delete_databases()

sys.exit(0)