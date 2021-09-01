import sys
from db import Database
from interface import GUI

# ----------------------------------------------------------------------------

db = Database(noisy=True, logging=True)
gui = GUI(db)
gui.run()
sys.exit(0)
