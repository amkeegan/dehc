from datetime import datetime, timezone
import random
import sys
from cloudant import couchdb
from cloudant.document import Document
from globals import read

# ----------------------------------------------------------------------------

class Database:
    def __init__(self, config: str = "db", *, logging: bool = True, 
    noisy: bool = True):
        '''Creates a database object.'''
        self.config = read(config)
        self.noisy = noisy
        self.logging = logging
        if self.logging == True:
            with couchdb(**self.config) as client:
                if "logging" not in client.all_dbs():
                    client.create_database("logging")
    
    def _say(self, msg: str):
        '''Prints msg if database is set to be noisy.'''
        if self.noisy == True:
            print(msg)

    def _gettime(self):
        '''Returns a timestamp as a string.'''
        ts = datetime.now(timezone.utc)
        return f"{ts.year}-{ts.month:02d}-{ts.day:02d} {ts.hour:02d}:{ts.minute:02d}:{ts.second:02d} {ts.tzname()}"

    def _log(self, msg: str):
        '''Creates a log entry for a database transaction.'''
        ts = self._gettime()
        if self.logging == True:
            id = self.doc_get_id(prefix="log-")
            with couchdb(**self.config) as client:
                with Document(client["logging"], id) as doc:
                    doc["msg"] = msg
                    doc["timestamp"] = ts
        self._say(f"{ts} | {msg}")
    
    def db_create(self, dbname: str = "dehc"):
        '''Creates the dehc database.'''
        with couchdb(**self.config) as client:
            if dbname not in client.all_dbs():
                client.create_database(dbname)
                self._log(f"New db: {dbname}")
    
    def db_delete(self, dbname: str = "dehc"):
        '''Deletes the dehc database.'''
        with couchdb(**self.config) as client:
            if dbname in client.all_dbs():
                client.delete_database(dbname)
                self._log(f"Del db: {dbname}")

    def db_query(self, field: str, value: str, sortkey: str, dbname: str = "dehc") -> list[dict]:
        '''Returns all documents with field matching value.'''
        with couchdb(**self.config) as client:
            db = client[dbname]
            result = db.get_query_result(selector={field:{"$eq":value}})
            result = [row for row in result]
            result.sort(key=lambda x: x[sortkey])
        self._say(f"{self._gettime()} | Queried '{field}' of '{value}'")
        return result

    def doc_edit(self, data: dict, id: str = "", dbname: str = "dehc"):
        '''Creates or edits a document to the dehc database.'''
        id = self.doc_get_id() if id == "" else id
        fields, values = [], []
        with couchdb(**self.config) as client:
            with Document(client[dbname], id) as doc:
                for key, value in data.items():
                    if doc.get(key, "") != value: 
                        doc[key] = value
                        fields.append(key)
                        values.append(value)
        self._log(f"Edit doc: {id} {fields} -> {values}")
            
    def doc_delete(self, id: str, dbname: str = "dehc"):
        '''Deletes a document from the dehc database'''
        with couchdb(**self.config) as client:
            with Document(client[dbname], id) as doc:
                doc["_deleted"] = True
        self._log(f"Del doc: {id}")
    
    def doc_get_id(self, prefix: str = ""):
        n = hex(random.randint(0, 281474976710656))[2:]
        return prefix+"0"*(12-len(n))+n
