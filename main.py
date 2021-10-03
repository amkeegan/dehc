'''The script that starts the main DEHC application.'''

import argparse
import sys

import apps.ems as ae
import mods.database as md
import mods.log as ml

# ----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Starts the Digital Evacuation Handling Center')
parser.add_argument('-a','-auth', type=str, default="db_auth.json", help="relative path to database authentication file", metavar="PATH")
parser.add_argument('-b','-book', type=str, default="bookmarks.json", help="relative path to EMS screen bookmarks", metavar="PATH")
parser.add_argument('-l','-logg', type=str, default="DEBUG", help="minimum level of logging messages that are printed: DEBUG, INFO, WARNING, ERROR, CRITICAL, or NONE", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL","NONE"], metavar="LEVL")
parser.add_argument('-n','-name', type=str, default="dehc", help="which database namespace to use", metavar="NAME")
parser.add_argument('-s','-sche', type=str, default="db_schema.json", help="relative path to database schema file", metavar="PATH")
args = parser.parse_args()

# ----------------------------------------------------------------------------

logger = ml.get(name="Main", level=args.l)
logger.debug("Application has started.")

db = md.DEHCDatabase(config=args.a, level=args.l, namespace=args.n, schema=args.s, quickstart=True)
app = ae.EMS(db=db, bookmarks=args.b, level=args.l, autorun=True)

logger.debug("Application is ending.")
sys.exit(0)
