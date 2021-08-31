import json
import os.path

# ----------------------------------------------------------------------------

def read(name: str) -> dict:
    '''Reads name.json in root folder and returns contents.'''
    jsonfile = os.path.join(os.path.split(__file__)[0], name+".json")
    with open(jsonfile, "r") as f:
        data = f.read()
        return json.loads(data)
