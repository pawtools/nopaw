#!/usr/bin/env python

import sys
import os
from uuid import uuid1 as _uuid_
from pymongo import MongoClient
from pathlib import Path
import numbers

def _file_reader(meta_data):
    with open(meta_data["file_path"]) as data_file:
        return data_file.read()

def _int_reader(meta_data):
    return int(meta_data["data"])

def _float_reader(meta_data):
    return float(meta_data["data"])

def _complex_reader(meta_data):
    return complex(meta_data["data"])

def _string_reader(meta_data):
    return meta_data["data"]

class PawTask:
    def __init__(self, parent, task):
        self.parent = parent
        self.task = task
        self.cached_data = dict()
    def __getitem__(self, key):
        return self.parent.read_data(self.task["meta_data"][key])
    def update_status(self, status):
        self.parent.update_status(status)
    

class PawClient:
    def __init__(self, dbhost, dbport, dbname):
        assert dbport.find('.') < 0
        dbport = int(dbport)
        self.dbhost = dbhost
        self.dbport = dbport
        self.dbname = dbname
        self.readers = dict()
        self.add_reader("inline int", _int_reader)
        self.add_reader("inline float", _float_reader)
        self.add_reader("inline complex", _complex_reader)
        self.add_reader("inline string", _string_reader)
        self.add_reader("file", _file_reader)

    def add_reader(self, name, func):
        assert callable(func)
        self.readers[name] = func

    def read_data(self, meta_data):
        return self.readers[meta_data["type"]](meta_data)

    def _file_path(self, data):
        #TODO: Keep info on what node this is on, so that even local files can be
        #shared over the network. For now, just assume this is a shared directory
        return {"type":"file", "file_path":data}
    def _add_string(self, data):
        #TODO: For now, assume all string data will be small enough to inline.
        return {"type":"inline string", "data":str(data)}
    def _add_number(self, data):
        type_signatures = { int : "inline int", 
                            float: "inline float", 
                            complex: "inline complex" }
        string_type = type_signatures[type(data)]
        return {"type": string_type, "data":str(data)}

    #The intention here is that a task uses this to create the data representation that
    #gets added to the database with the task, returning a hash destened to be a json
    #blob. 
    def prepare_data(self, data):
        if callable(getattr(data, 'prepare_paw_data', None)):
            return data.prepare_paw_data()

        #The hope and dream is that tasks prepare their own data in the call above
        #If not, fall through to catch most basic types.
        if isinstance(data, numbers.Number):
            return self._add_number(data)
        else:
            builtins = { str : self._add_string,
                         Path : self._add_string }
            return builtins[type(data)](data)

    def add_task(self, **task_data):
        meta_data = {key:self.prepare_data(value) for key,value in task_data.items()}
        document = {
            "_id" : _uuid_(),
            "meta_data": meta_data,
            "status": "not started"
        }

        mongodb = self.open_client

        db = mongodb[self.dbname]
        cl = db[self.dbname]
        cl.insert_one(document)

    def update_status(task, new_string):
        query = {"_id":task["_id"]}
        update = {"status": str(new_string)}
        mongodb = self.open_client

        db = mongodb[self.dbname]
        cl = db[self.dbname]
        cl.update_one(query, update)

    def get_task(self):
        from pymongo import ReadConcern
        mongodb = self.open_client
        #db = mongodb[self.dbname]
        db = get_database(name=self.dbname, read_concern=ReadConcern("linearizable")
        cl = db[self.dbname]
        task = cl.find_one()
        self.update_status(task, "started")
        return PawTask(self,task)

    #Try hitting the database with a cheap operation to see if it is there. Mostly for testing and debugging
    def check_connection(self):
        from pymongo.errors import ConnectionFailure
        try:
            self.open_client.admin.command('ismaster')
        except ConnectionFailure:
            return False
        return True

    def connect(self):
        self.open_client = MongoClient(self.dbhost, self.dbport)

    def close(self):
        try:
            self.open_client.close()
            del self.open_client
        except AttributeError:
            return

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

import unittest

class PawTests(unittest.TestCase):
    def setUp(self):
        self.client = PawClient("127.0.0.1", "27017", "tester")
    def tearDown(self):
        with self.client as open_db:
            open_db.open_client.drop_database("tester")
        del(self.client)

    def round_trip(self, x):
        meta =  self.client.prepare_data(x)
        read = self.client.read_data(meta)
        self.assertEqual(x,read)

    def test_insert_task(self):
        in_data = (42, 4.2, complex(4+2j), "string data")
        with self.client as open_db:
            if not open_db.check_connection():
                unittest.SkipTest("No local DB to test against")
            for test_data in in_data:
                open_db.add_task(k=42)
            self.assertTrue(True)

    def test_get_task(self):
        in_data = (42, 4.2, complex(4+2j), "string data")
        with self.client as open_db:
            if not self.client.check_connection():
                unittest.SkipTest("No local DB to test against")
            for test_number in in_data:
                test_number = 42
                open_db.add_task(k=test_number)
                k_task = open_db.get_task()
                k_data = k_task["k"]
                self.assertEqual(test_number, k_data)

    def test_builtin_datatypes(self):
        in_data = (42, 4.2, complex(4+2j), "string data")
        for data_object in in_data:
            self.round_trip(data_object)

    def test_custom_datatype(self):
        class TestHelper:
            def __init__(self,x):
                self.data = x
            def prepare_paw_data(self):
                return {"type":"custom_test", "data":self.data}
            def reader(x):
                return TestHelper(x["data"])
            def __eq__(self,other):
                return self.data == other.data
        self.client.add_reader("custom_test", TestHelper.reader)
        self.round_trip(TestHelper("test_data"))


if __name__ == "__main__":
    unittest.main()
    sys.exit()
