'''The module containing objects that manage the CouchDB database.'''

import datetime
import json
import random

from ibmcloudant import CouchDbSessionAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1, Document

# ----------------------------------------------------------------------------

class Database:
    '''A class which enables communication with a CouchDB database.
    
    This class is application agnostic and only performs basic operations. For helper methods specific to the DEHC application, use the DEHCDatabase class down below.
    
    client: The Cloudant-CouchDB client object.
    loud: If true, database transactions will be logged to console.
    '''

    def __init__(self, config: str, loud: bool = False):
        '''Constructs a Database object.
        
        config: Path to .json file containing database server credentials.
        loud: If true, database transactions will be logged to console.
        '''
        with open(config, "r") as f:
            data = json.loads(f.read())
        auth = CouchDbSessionAuthenticator(username=data['user'], password=data['pass'])
        self.client = CloudantV1(authenticator=auth)
        self.client.set_service_url(data['url'])
        self.loud = loud


    def database_create(self, dbname: str):
        '''Creates a new database.
        
        dbname: Name of the database to create.
        '''
        self.client.put_database(db=dbname)
        self._log(f"New db {dbname}")


    def database_delete(self, dbname: str):
        '''Deletes an existing database.
        
        dbname: Name of the database to delete.
        '''
        self.client.delete_database(db=dbname)
        self._log(f"Del db {dbname}")


    def database_exists(self, dbname: str):
        '''Returns whether or not a database exists.
        
        dbname: Name of the database to check.
        '''
        try:
            response = self.client.get_database_information(db=dbname).get_status_code()
            if response == 200:
                return True
            else:
                return False
        except:
            return False


    def database_list(self):
        '''Returns a list of active databases.'''
        return self.client.get_all_dbs().get_result()


    def design_create(self):
        '''Creates a new design document.'''
        pass


    def design_delete(self):
        '''Deletes an existing design document.'''
        pass


    def design_edit(self):
        '''Edits an existing design document.'''
        pass


    def design_exists(self):
        '''Returns whether or not a design document exists.'''
        pass


    def design_get(self):
        '''Retrieves a design document from a database and returns it.'''
        pass


    def design_list(self):
        '''Returns a list of all design documents in a database.'''
        pass


    def design_query(self):
        '''Queries a database using a design document's view.'''
        pass


    def design_queries(self):
        '''Runs multiple queries on a database using various views.'''
        pass


    def document_create(self, dbname: str, id: str, doc: dict):
        '''Creates a new document.
        
        dbname: Name of database to create document in.
        id: The UUID of document to create.
        doc: The contents of the document.
        '''
        doc = Document(id=id, **doc)
        res = self.client.post_document(db=dbname, document=doc)
        self._log(f"New doc {dbname} {id}")


    def document_delete(self, dbname: str, id: str):
        '''Deletes an existing document.
        
        dbname: Name of database to delete document in.
        id: The UUID of document to delete.
        '''
        doc = self.client.get_document(db=dbname, doc_id=id).get_result()
        self.client.delete_document(db=dbname, doc_id=id, rev=doc["_rev"])
        self._log(f"Del doc {dbname} {id}")


    def document_edit(self):
        '''Edits an existing document.'''
        pass


    def document_exists(self):
        '''Returns whether or not a document exists.'''
        pass


    def document_get(self):
        '''Retrieves a document from a database and returns it.'''
        pass


    def document_list(self):
        '''Returns a list of all documents in a database. Intensive!'''
        pass


    def documents_create(self):
        '''Creates multiple documents at once.'''
        pass


    def documents_delete(self):
        '''Deletes multiple documents at once.'''
        pass


    def documents_edit(self):
        '''Edits multiple documents at once.'''
        pass


    def documents_get(self):
        '''Retrieves multiple documents and returns them.'''
        pass


    def id_create(self, n: int = 1, length: int = 12, prefix: str = ""):
        '''Generates new UUIDs within Python and returns them.
        
        n: The number of UUIDs to create.
        length: The length of the UUID's hex component.
        prefix: Prefix for the UUID.
        '''
        ids = []
        for _ in range(0, n):
            hexstr = hex(random.randint(0, 16 ** length))[2:]
            id = prefix + "0" * (length - len(hexstr)) + hexstr
            ids.append(id)
        return ids


    def id_get(self, n: int = 1, prefix: str = ""):
        '''Retrieves a new UUID from CouchDB and returns it.
        
        prefix: Prefix to add to the UUID.'''
        response = self.client.get_uuids(count=n).get_result()['uuids']
        for index, id in enumerate(response):
            response[index] = prefix+id
        return response


    def index_create(self):
        '''Creates a new MongoDB-style index.'''
        pass


    def index_delete(self):
        '''Deletes an existing MongoDB-style index.'''
        pass


    def index_edit(self):
        '''Edits an existing MongoDB-style index.'''
        pass


    def index_exists(self):
        '''Returns whether or not a MongoDB-style index exists.'''
        pass


    def index_get(self):
        '''Retrieves a MongoDB-style index and returns it.'''
        pass


    def index_query(self):
        '''Queries a database using MongoDB-style selectors & indexes.'''
        pass


    def server_check(self):
        '''Returns whether or not the CouchDB server is accessible.'''
        try:
            response = self.client.get_up_information().get_result()
            if response['status'] == 'ok':
                return True
            return False
        except:
            return False


    def _log(self, msg: str):
        '''Logs a timestamped message to the console.
        
        msg: Message to log.
        '''
        if self.loud == True:
            ts = datetime.datetime.now(datetime.timezone.utc)
            ts = f"{ts.year}-{ts.month:02d}-{ts.day:02d} {ts.hour:02d}:{ts.minute:02d}:{ts.second:02d}"
            if self.loud == True:
                print(f"{ts} | {msg}")


    def __repr__(self):
        '''Returns the canonical representation of a Database.'''
        pass

# ----------------------------------------------------------------------------

class DEHCDatabase:
    '''A class which handles database transactions in DEHC applications.
    
    This class is specific to DEHC and is the one to import into the apps. Importing the Database class up above should not be necessary.'''

    def __init__(self):
        '''Constructs a DEHCDatabase object.'''
        pass

    def __repr__(self):
        '''Returns the canonical representation of a DEHCDatabase.'''
        pass

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    db = Database(config="database.json", loud=True)

    # Check if the server is online
    if db.server_check() == True:
        
        # Create a database
        db.database_create(dbname="items")

        # Confirms database exists
        print(db.database_exists(dbname="items"))

        # Lists all databases
        print(db.database_list())

        # Create IDs two different ways
        id1, = db.id_create(prefix="Person-")
        id2, = db.id_get(prefix="Person-")

        # Create two new documents
        db.document_create(dbname="items", id=id1, doc={"name": "Alice", "age": "27"})
        db.document_create(dbname="items", id=id2, doc={"name": "Bob", "age": "26"})

        # Delete one of the documents
        db.document_delete(dbname="items", id=id1)

        # Delete the datbase
        db.database_delete(dbname="items")

    sys.exit(0)

# ----------------------------------------------------------------------------