import datetime
import json
import os
import random

from cloudant import couchdb
from cloudant.document import Document

# ----------------------------------------------------------------------------

class Database:
    '''
    Object which manages connections to and transactions with a CloudDB database.
    This class is application agnostic, simply providing database CRUD functions.
    For the DEHC app specifically, use DEHC_Database instead.
    '''
    def __init__(self, *, url: str, name: str, user: str, passwd: str, log: bool = True, loud: bool = True):
        '''A Database object which manages connections & transactions to a couchdb database.'''
        self.name = name
        self.url = url
        self.user = user
        self.passwd = passwd
        self.log = log
        self.logname = self.name+"-log"
        self.loud = loud

    def db_create(self):
        '''Creates the couchdb database.'''
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            if self.log == True and self.logname not in client.all_dbs():
                client.create_database(self.logname)
                self._log_(f"New db {self.logname}")
            if self.name not in client.all_dbs():
                client.create_database(self.name)
                self._log_(f"New db {self.name}")

    def db_delete(self, *, includelog: bool = False):
        '''Deletes the couchdb database.'''
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            if self.name in client.all_dbs():
                client.delete_database(self.name)
                self._log_(f"Del db {self.name}")
            if includelog == True and self.logname in client.all_dbs():
                client.delete_database(self.logname)
                self.log = False
                self._log_(f"Del db {self.logname}")

    def db_dump(self) -> list[dict]:
        '''Returns all documents from the couchdb database. Resource intensive!'''
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            db = client[self.name]
            docs = db.all_docs()['rows']
            self._log_(msg=f"Query *", nolog=True)
            return docs

    def db_query(self, *, selector: dict = {}, fields: list[str] = [], sort: list = []) -> list[dict]:
        '''Returns some documents from the couchdb database.'''
        selector = {'_id': {'$exists': True}} if selector == {} else selector
        fields = None if fields == [] else fields
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            db = client[self.name]
            docs = db.get_query_result(selector=selector, fields=fields, sort=sort, raw_result=True)['docs']
            self._log_(msg=f"Query {'*' if fields == None else fields} where {'*'if selector == {'_id': {'$exists': True}} else selector} {'' if sort == [] else 'sorted by '+str(sort)}", nolog=True)
            return docs

    def doc_get(self, *, id: str, fields: list[str] = None) -> dict:
        '''Returns a single document from the couchdb database.'''
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            data = client[self.name][id]
            if fields != None:
                data = {field: data[field] for field in fields}
                self._log_(msg=f"Get doc {id} {fields}", nolog=True)
            else:
                data = dict(data)
                self._log_(msg=f"Get doc {id}", nolog=True)
            return data

    def doc_edit(self, *, id: str, data: dict):
        '''Creates or edits an existing document in the couchdb database.'''
        fields, values = [], []
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            with Document(client[self.name], id) as doc:
                for key, value in data.items():
                    if doc.get(key, "") != value:
                        doc[key] = value
                        fields.append(key)
                        values.append(value)
            self._log_(f"Edit doc {id} {fields} -> {values}")

    def doc_delete(self, *, id: str):
        '''Deletes a document in the couchdb database.'''
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            with Document(client[self.name], id) as doc:
                doc["_deleted"] = True
            self._log_(f"Del doc {id}")

    def index_create(self, *, id: str, name: str, fields: list):
        '''Creates an index within the couchdb database.'''
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            db = client[self.name]
            names = [index.name for index in db.get_query_indexes()]
            if name not in names:
                db.create_query_index(design_document_id=id, index_name=name, fields=fields)
                self._log_(f"New idx {id} {name} {fields}")
    
    def index_delete(self, *, id: str, name: str):
        '''Deletes an index within the couchdb database.'''
        with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
            db = client[self.name]
            db.delete_query_index(design_document_id=id, index_type='json', index_name=name)
            self._log_(f"Del idx {id} {name}")

    def doc_id(self, *, prefix: str = "") -> str:
        '''Generates a random id.'''
        n = hex(random.randint(0, 281474976710656))[2:]
        return prefix+"0"*(12-len(n))+n

    def _log_(self, msg: str, *, nolog: bool = False):
        '''Logs a timestamped message if logging enabled. Outputs to terminal if Database is loud.'''
        if self.loud == True or self.log == True:
            ts = datetime.datetime.now(datetime.timezone.utc)
            ts = f"{ts.year}-{ts.month:02d}-{ts.day:02d} {ts.hour:02d}:{ts.minute:02d}:{ts.second:02d}"
            if self.loud == True:
                print(f"{ts} | {msg}")
            if self.log == True and nolog == False:
                id = self.doc_id(prefix="log-")
                with couchdb(user=self.user, passwd=self.passwd, url=self.url) as client:
                    with Document(client[self.logname], id) as doc:
                        doc["ts"] = ts
                        doc["msg"] = msg

# ----------------------------------------------------------------------------

class DEHC_Database:
    '''
    Object which manages the DEHC database.
    Contains helper functions, validation, and some hard-coded fields specific to DEHC.
    Uses the Database class above to communicate with CouchDB.
    '''
    def __init__(self, *, create: bool = True):
        '''An object which connects the DEHC application and database API.'''
        jsonpath = os.path.join(os.path.split(__file__)[0], "db.json")
        with open(jsonpath, "r") as f:
            data = json.loads(f.read())
        self.db = Database(url=data['url'], name='dehc', user=data['user'], passwd=data['passwd'], log=False, loud=True)
        if create == True:
            self.db_create()
    
    def db_create(self):
        '''Creates the DEHC database.'''
        self.db.db_create()
    
    def db_delete(self):
        '''Deletes the DEHC database.'''
        self.db.db_delete(includelog=True)

    def db_search(self, *, category: str = None, selector: dict = {}, fields: list[str] = [], sort: list = [], pythonsort: bool = True, flatten: bool = False) -> list:
        '''Queries the DEHC database and returns data for all relevent items.'''
        selector_c = selector.copy()
        if category != None:
            selector_c['category'] = {'$eq': category}
        result = []
        if pythonsort == True:
            result = self.db.db_query(selector=selector_c, fields=fields)
            for sfield in sort[::-1]:
                result.sort(key=lambda x: x[sfield])
        else:
            if sort != []:
                index_id = self.db.doc_id(prefix=f"idx-")
                index_name = ", ".join(sort)
                self.db.index_create(id=index_id, name=index_name, fields=sort)
            result =  self.db.db_query(selector=selector_c, fields=fields, sort=sort)
        if len(fields) == 1 and flatten == True:
            field, = fields
            result = [row[field] for row in result]
        return result

    def item_add(self, *, category: str, data: dict = {}) -> str:
        '''Adds an item to the DEHC database and returns its id.'''
        id = self.db.doc_id(prefix=f"{category}-")
        data_c = data.copy()
        data_c['category'] = category
        data_c['contains'] = []
        self.db.doc_edit(id=id, data=data_c)
        return id
    
    def item_edit(self, *, id: str, data: dict = {}):
        '''Edits an existing item in the DEHC database.'''
        data_c = data.copy()
        self.db.doc_edit(id=id, data=data_c)
    
    def item_get(self, *, id: str, fields: list[str] = None) -> dict:
        '''Gets the data for a single item in the DEHC database.'''
        return self.db.doc_get(id=id, fields=fields)

    def item_delete(self, *, id: str):
        '''Deletes an item from the database.'''
        self.db.doc_delete(id=id)
    
    def container_add(self, *, container: str, item: str):
        '''Puts an item into a container.'''
        if container != item:
            doc = self.db.doc_get(id=container, fields=['contains'])
            contains = doc['contains']
            if item not in contains:
                contains.append(item)
                self.db.doc_edit(id=container, data={'contains': contains})
    
    def container_remove(self, *, container: str, item: str):
        '''Removes an item from a container.'''
        doc = self.db.doc_get(id=container, fields=['contains'])
        contains = doc['contains']
        if item in contains:
            contains.remove(item)
            self.db.doc_edit(id=container, data={'contains': contains})
    
    def container_get(self, *, container: str) -> list:
        '''Returns a list of items that are contained by the container.'''
        return self.db.doc_get(id=container, field=['contains'])['contains']
    
    def container_find(self, *, item: str, category: str = None) -> list:
        '''Returns a list of containers that an item is contained by.'''
        selector = {'contains': {"$all": [item]}}
        query = self.db_search(category=category, selector=selector, fields=["_id"], flatten=True)
        return query

# ----------------------------------------------------------------------------