import json
import os.path

# ----------------------------------------------------------------------------

G_FIELDS_EVACUEE = ["Family Name","Given Name(s)","Sex","Date of Birth",
"Passport Number","Nationality","Home Address","Destination Address",
"Home Contact Number","Destination Contact Number","Next Of Kin Family Name",
"Next Of Kin Given Name","Next Of Kin Address","Next Of Kin Contact Number",
"Travelling With Next Of Kin","Requires Medical Attention",
"Authority To Release Information","Evacuee Searched","Evacuee Search Date",
"Baggage Searched","Baggage Search Date","Documentation Complete",
"Medical Complete","Screening Complete","Accomodation","Date Of Flight",
"Report Time","Flight Number","Depart Time","Place of Registration",
"Registration Date","Registered Number","Registered Number System","Misc"]

# ----------------------------------------------------------------------------

def read(name: str) -> dict:
    '''Reads name.json in root folder and returns contents.'''
    jsonfile = os.path.join(os.path.split(__file__)[0], name+".json")
    with open(jsonfile, "r") as f:
        data = f.read()
        return json.loads(data)
