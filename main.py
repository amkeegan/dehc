'''The script that starts the main DEHC application.'''

import argparse
import sys

import apps.ems as ae
import mods.database as md
import mods.log as ml

# ----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Starts the Digital Evacuation Handling Center')
parser.add_argument('-a','-auth', type=str, default="db_auth.json", help="relative path to database authentication file", metavar="PATH")
args = parser.parse_args()

# ----------------------------------------------------------------------------

level = "INFO"

logger = ml.get(name="Main", level=level)
logger.debug("Application has started.")

db = md.DEHCDatabase(config=args.a, level=level, quickstart=True)
app = ae.EMS(db=db, level=level, autorun=True)

# ----------------------------------------------------------------------------

logger.debug("Application is ending.")
sys.exit(0)
