#!/usr/bin/env python

import sys
import os
from time import time
from datetime import datetime
from pymongo import MongoClient


print("pyscript recieved args:\n{}".format(
    sys.argv))

operation = sys.argv[1]
dbhost = sys.argv[2]
dbport = sys.argv[3]
dbname = sys.argv[4]

assert operation in {"read","write"}
assert dbport.find('.') < 0
dbport = int(dbport)

mongodb = MongoClient(dbhost, dbport)

db = mongodb[dbname]
cl = db[dbname]

print("pyscript starting {}".format(
    datetime.fromtimestamp(time())))

try:

    print("sync starting {}".format(
        datetime.fromtimestamp(time())))

    if operation == "write":

        thedata = """Jem says hello
Jem says hi
Every day Jemerson loves to try
Things like reading, writing, climbing in a tree
He's buzzing around like a bizzy bee
bzzzzzzzzzzzzzzzzzzz
 - jem
"""

        document = {
            "_id"   : _uuid_,
            "data"  : thedata,
            "state" : "final",
        }

        cl.insert_one(document)

    elif operation == "read":
        thedata = cl.find_one()

    print("sync stopping {}".format(
        datetime.fromtimestamp(time())))

except Exception as e:
    mongodb.close()
    print(e)


print("pyscript stopping {}".format(
    datetime.fromtimestamp(time())))
