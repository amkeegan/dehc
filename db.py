import random
from cloudant import couchdb
from cloudant.document import Document
from tools import read

# ----------------------------------------------------------------------------

class Database:
    def __init__(self, config="db", noisy=True):
        '''Creates a database object.'''
        self.config = read(config)
        self.noisy = noisy
    
    def _say(self, msg):
        '''Prints msg if database is set to be noisy.'''
        if self.noisy == True:
            print(msg)
    
    def db_create(self, dbname: str = "dehc"):
        '''Creates the dehc database.'''
        with couchdb(**self.config) as client:
            client.create_database(dbname)
            self._say(f"Created database \"{dbname}\".")
    
    def db_delete(self, dbname: str = "dehc"):
        '''Deletes the dehc database.'''
        with couchdb(**self.config) as client:
            client.delete_database(dbname)
            self._say(f"Deleted database \"{dbname}\".")

    def db_query(self, field, value, dbname: str = "dehc"):
        '''Returns all documents with field matching value.'''
        with couchdb(**self.config) as client:
            db = client[dbname]
            result = db.get_query_result({field:{"$eq":value}})
            result = [row for row in result]
        self._say(f"Returned docs with \"{field}\" of \"{value}\".")
        return result

    def doc_edit(self, data: dict, id: str = "", dbname: str = "dehc"):
        '''Creates or edits a document to the dehc database.'''
        id = self.doc_get_id() if id == "" else id
        with couchdb(**self.config) as client:
            with Document(client[dbname], id) as doc:
                for key, value in data.items():
                    doc[key] = value
        self._say(f"Edited document with id \"{id}\".")
            
    def doc_delete(self, id: str, dbname: str = "dehc"):
        '''Deletes a document from the dehc database'''
        with couchdb(**self.config) as client:
            with Document(client[dbname], id) as doc:
                doc["_deleted"] = True
        self._say(f"Deleted document with id \"{id}\".")
    
    def doc_get_id(self, prefix=""):
        n = hex(random.randint(0, 281474976710656))[2:]
        n = prefix+"0"*(12-len(n))+n
        return n

x = Database()
x.doc_get_id()
