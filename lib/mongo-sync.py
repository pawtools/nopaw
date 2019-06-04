#!/usr/bin/env python

import sys
import os
from uuid import uuid1 as _uuid_
from time import time
from datetime import datetime
from pymongo import MongoClient


print("pyscript starting {}".format(datetime.fromtimestamp(time())))
print("pyscript recieved args:\n{}".format(sys.argv))

if __name__ == "__main__":
    operation = sys.argv[1]
    dbhost = sys.argv[2]
    dbport = sys.argv[3]
    dbname = sys.argv[4]
    data_factor = sys.argv[5]

    assert operation in {"read","write"}
    assert dbport.find('.') < 0
    assert data_factor.find('.') < 0
    dbport = int(dbport)
    data_factor = int(data_factor)

    thedata = """Jem says hello
    Jem says hi
    Every day Jemerson loves to try
    Things like reading, writing, climbing in a tree
    He's buzzing around like a bizzy bee
    bzzzzzzzzzzzzzzzzzzz
     - jem
    """ * data_factor

    mongodb = MongoClient(dbhost, dbport)
    db = mongodb[dbname]
    cl = db[dbname]

    if operation == "write":

        document = {
            "_id"   : _uuid_(),
            "data"  : thedata,
            "state" : "final",
        }

        print("sync starting {}".format(datetime.fromtimestamp(time())))
        cl.insert_one(document)
        print("sync stopping {}".format(datetime.fromtimestamp(time())))

    elif operation == "read":

        print("sync starting {}".format(datetime.fromtimestamp(time())))
        readdata = cl.find_one()
        print("sync stopping {}".format(datetime.fromtimestamp(time())))

        if thedata == readdata['data']:
            print("Data was verified")

        else:
            print("This data was not verified: ")
            print(readdata['data'])

    mongodb.close()
    print("pyscript stopping {}".format(datetime.fromtimestamp(time())))

