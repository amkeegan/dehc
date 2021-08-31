import sys
from db import Database
from interface import GUI

# ----------------------------------------------------------------------------

db = Database(noisy=False)
gui = GUI(db)
gui.run()

sys.exit(0)
