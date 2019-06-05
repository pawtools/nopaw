#!/usr/bin/env python

import sys
import os
from uuid import uuid1 as _uuid_
from pymongo import MongoClient

# FIXME paw "scripts" should import from pawtools!
#from pawtools import get_logger

print("pyscript recieved args:\n{}".format(
    sys.argv))

if __name__ == "__main__":

    dbhost = sys.argv[1]
    dbport = sys.argv[2]
    dbname = sys.argv[3]
    data_factor = sys.argv[4]
    nreplicates = sys.argv[5]
    task_operation = sys.argv[5]

    assert dbport.find('.') < 0
    dbport = int(dbport)
    assert data_factor.find('.') < 0
    data_factor = int(data_factor)
    print("data_factor: {}".format(data_factor))

    thedata = """Jem says hello
    Jem says hi
    Every day Jemerson loves to try
    Things like reading, writing, climbing in a tree
    He's buzzing around like a bizzy bee
    bzzzzzzzzzzzzzzzzzzz
     - jem
    """ * data_factor

    document = {
        "_id" : _uuid_(),
        "data": thedata,
        "task": False,    # not a task
    }

    mongodb = MongoClient(dbhost, dbport)

    db = mongodb[dbname]
    cl = db[dbname]
    cl.insert_one(document)
    mongodb.close()
