import json
import ibm_cloud_sdk_core
from ibm_cloud_sdk_core import api_exception
from ibmcloudant import CouchDbSessionAuthenticator
from ibmcloudant.cloudant_v1 import BulkDocs, CloudantV1, Document, ReplicationDatabase, ReplicationDatabaseAuth, ReplicationDatabaseAuthIam, ReplicationDocument
import time 
import copy
import uuid
import argparse
import base64


parser = argparse.ArgumentParser(description='sets up repliaction from central server to local machine.')
#parser.add_argument('-la','--localauth', type=str, default="db_auth.json", help="relative path to database authentication file for the local db", metavar="LOCALPATH")
#parser.add_argument('-ra','--remoteauth', type=str, default="db_auth.json", help="relative path to database authentication file for the remote db", metavar="REMOTEPATH")
parser.add_argument('-n','--name', type=str, default="dehc", help="which database namespace to use", metavar="NAME")

args = parser.parse_args()

localusername = "admin"
localpass = "Creative"
localserver = "http://127.0.0.1:5984/"
remoteserver ="http://10.8.0.1:5984/"
dblist = ["items", "containers", "config", "ids", "files"]

def add_replication(dbcon,source_host,destination_host,db):
    print(f"Replicating from {source_host} to {destination_host} database '{db}'")
    replication_json_dict = {
        '_id': '.',
        "user_ctx": {
            "name": "admin",
            "roles": [
            "_admin",
            "_reader",
            "_writer"
            ]},        
        'source': {
            'url': '.',
            'headers': {
                'Authorization': '.'
            }
        },
        'target': {
            'url': '.',
            'headers': {
                'Authorization': '.'
            }
        },
        'create_target': 'true',
        'continuous': 'true',
        'owner': 'admin'
    }

    replication_doc = copy.deepcopy(replication_json_dict)

    replication_doc['_id'] = "auto_" + str(uuid.uuid1())
    replication_doc['source']['url'] = source_host + db
    replication_doc['source']['headers']['Authorization'] = 'Basic ' + base64.b64encode(('admin'+':'+'Creative').encode()).decode()
    replication_doc['target']['url'] = destination_host + db
    replication_doc['target']['headers']['Authorization'] = 'Basic ' + base64.b64encode(('admin'+':'+'Creative').encode()).decode()
    replication_doc['create_target'] = True
    replication_doc['continuous'] = True
    replication_doc['owner'] = 'admin'



    try:
        dbcon.put_document(db='_replicator', doc_id=replication_doc['_id'], document=json.dumps(replication_doc))
    except ibm_cloud_sdk_core.api_exception.ApiException as err:
        if err.code == 409:
            print('Replication document already exists')
        else:
            print('Undhandled exception...')
            print(err)
if __name__ == "__main__":
    local_auth = CouchDbSessionAuthenticator(username=localusername, password=localpass)
    local_couchdb_connection = CloudantV1(authenticator=local_auth)
    local_couchdb_connection.set_service_url(localserver)
    

    local_info = local_couchdb_connection.get_all_dbs().get_result()
    for working_database in dblist:
        current_database = args.name + "-" + working_database
        print("Deleting " + current_database, end =" ")
        try:
            local_couchdb_connection.delete_database(db=current_database)
            print("ok")
        except:
            print("failed for some reason")
    
        add_replication(local_couchdb_connection,remoteserver,localserver,current_database)        
        time.sleep(3) #let the local copy get created before trying to setup the reverse. It still works but it fails initially and waits before retrying.
        add_replication(local_couchdb_connection,localserver,remoteserver,current_database)                    
    print('Done')    
