'''The script that starts the main DEHC application.'''

import argparse
import sys

if sys.version_info.major == 3 and sys.version_info.minor == 9:
    import apps.ems as ae
    import mods.database as md
    import mods.log as ml
    import mods.dehc_hardware as hw
else:
    print("This application must be run using Python 3.9.X.")
    sys.exit(1)

# ----------------------------------------------------------------------------

if __name__ == "__main__": # Multiprocessing library complains if this guard isn't used
    
    DBVERSION = "211013"
    parser = argparse.ArgumentParser(description='Starts the Digital Evacuation Handling Center')
    parser.add_argument('-a','--auth', type=str, default="db_auth.json", help="relative path to database authentication file", metavar="PATH")
    parser.add_argument('-b','--book', type=str, default="bookmarks.json", help="relative path to EMS screen bookmarks", metavar="PATH")
    parser.add_argument('-l','--logg', type=str, default="DEBUG", help="minimum level of logging messages that are printed: DEBUG, INFO, WARNING, ERROR, CRITICAL, or NONE", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL","NONE"], metavar="LEVL")
    parser.add_argument('-n','--name', type=str, default="dehc", help="which database namespace to use", metavar="NAME")
    parser.add_argument('-s','--sche', type=str, default="db_schema.json", help="relative path to database schema file", metavar="PATH")
    parser.add_argument('-v','--vers', type=str, default=DBVERSION, help="schema version to expect", metavar="VERS")
    args = parser.parse_args()

    # ----------------------------------------------------------------------------

    logger = ml.get(name="Main", level=args.logg)
    logger.info("Application has started.")

    hardware = None

    try:
        hardware = hw.Hardware(makeNFCReader=True, makeBarcodeReader=True, makePrinter=True, makeScales=True)
    except RuntimeError: #TODO: determine if this is still valid, since __main__ check
        pass

    db = md.DEHCDatabase(config=args.auth, level=args.logg, namespace=args.name, schema=args.sche, quickstart=True, version=args.vers)
    app = ae.EMS(db=db, bookmarks=args.book, level=args.logg, autorun=True, hardware=hardware)

    if hardware is not None:
        hardware.terminateProcesses()

    logger.info("Application is ending.")
    sys.exit(0)
