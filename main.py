'''The script that starts the main DEHC application.'''

import sys

import apps.ems as ae
#import mods.database as md
import mods.log as ml

# ----------------------------------------------------------------------------

level = "DEBUG"
logger = ml.get(name="Main", level=level)
logger.debug("Application has started.")
#db = md.DEHCDatabase(config="db_auth.json", level=level, quickstart=True)

app = ae.EMS(level=level)

#db.databases_delete()
logger.debug("Application is ending.")
sys.exit(0)
