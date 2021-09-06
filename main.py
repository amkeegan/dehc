import sys
from tkinter.font import families

from db import DEHC_Database
from interface import IngestApp

# ----------------------------------------------------------------------------

db = DEHC_Database(create=False)
IngestApp(db=db).run()
sys.exit(0)

# ----------------------------------------------------------------------------