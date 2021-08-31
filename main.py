import sys
from db import Database
from interface import GUI

# ----------------------------------------------------------------------------

db = Database(noisy=True)
db.db_create()

gui = GUI(db)
gui.run()

db.db_delete()
sys.exit(0)
