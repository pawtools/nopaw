#!/usr/bin/env python

import sys
import os
from uuid import uuid1 as _uuid_
from time import time
from datetime import datetime
from pymongo import MongoClient

print("pyscript starting {}".format(datetime.fromtimestamp(time())))

operation = sys.argv[1]
dbhost = sys.argv[2]
dbport = sys.argv[3]
dbname = sys.argv[4]
print("pyscript recieved args:\n{}".format(sys.argv))

assert operation in {"read","write"}
assert dbport.find('.') < 0
dbport = int(dbport)

thedata = """Jem says hello
Jem says hi
Every day Jemerson loves to try
Things like reading, writing, climbing in a tree
He's buzzing around like a bizzy bee
bzzzzzzzzzzzzzzzzzzz
 - jem
"""

mongodb = MongoClient(dbhost, dbport)
db = mongodb[dbname]
cl = db[dbname]
print("sync starting {}".format(datetime.fromtimestamp(time())))

if operation == "write":
    document = {
        "_id"   : _uuid_(),
        "data"  : thedata,
        "state" : "final",
    }
    cl.insert_one(document)

elif operation == "read":
    readdata = cl.find_one()
    if thedata == readdata['data']:
        print("Data was verified")
    else:
        print("This data was not verified: ")
        print(readdata['data'])

print("sync stopping {}".format(datetime.fromtimestamp(time())))
mongodb.close()
print("pyscript stopping {}".format(datetime.fromtimestamp(time())))

