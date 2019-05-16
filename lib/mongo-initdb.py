#!/usr/bin/env python

import sys
import os
from uuid import uuid1 as _uuid_
from pymongo import MongoClient


print("pyscript recieved args:\n{}".format(
    sys.argv))

if __name__ == "__main__":
    dbhost = sys.argv[1]
    dbport = sys.argv[2]
    dbname = sys.argv[3]

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

    document = {
        "_id" : _uuid_(),
        "data": thedata,
    }

    mongodb = MongoClient(dbhost, dbport)

    db = mongodb[dbname]
    cl = db[dbname]
    cl.insert_one(document)
    mongodb.close()
