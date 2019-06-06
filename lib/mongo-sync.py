#!/usr/bin/env python

import sys
import os
from uuid import uuid1 as _uuid_
from time import time
from datetime import datetime
from pymongo import MongoClient, ReturnDocument


def get_task(collection, finder_id):
    locking_update = {
        {"$set":
          {"executor": finder_id,
           "state"   : "pending",
        }}
    }

    created_task_filter = {
        "type" : "task",
        "state": "created",
    }

    task = collection.find_one_and_update(
        state_filter,
        locking_update,
        return_document=ReturnDocument.AFTER,
    )

    return task

print("pyscript starting {}".format(datetime.fromtimestamp(time())))
print("pyscript recieved args:\n{}".format(sys.argv))

if __name__ == "__main__":
    dbhost = sys.argv[1]
    dbport = sys.argv[2]
    dbname = sys.argv[3]
    data_factor = sys.argv[4]

    assert dbport.find('.') < 0
    assert data_factor.find('.') < 0
    dbport = int(dbport)
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

    my_id = _uuid_()

    mongodb = MongoClient(dbhost, dbport)
    db = mongodb[dbname]
    cl = db[dbname]

    my_task = get_task(cl, my_id)
    my_operation = my_task["operation"]

    assert isinstance(my_task, dict)
    assert operation in {"read","write"}

    if operation == "write":

        task_update = {
            "data"  : thedata,
            "state" : "running",
        }

        print("sync starting {}".format(datetime.fromtimestamp(time())))

        cl.update_one(
            {"_id"  : my_task["_id"]},
            {"$set": task_update},
        )

        print("sync stopping {}".format(datetime.fromtimestamp(time())))

    elif operation == "read":

        print("sync starting {}".format(datetime.fromtimestamp(time())))
        readdata = cl.find_one({"type":"data"})
        print("sync stopping {}".format(datetime.fromtimestamp(time())))

        print("going to verify at runtime...")
        if thedata == readdata['data']:
            print("Data was verified")

        else:
            print("This data was not verified: ")
            print(readdata['data'])

    #mongodb.close()
    print("pyscript stopping {}".format(datetime.fromtimestamp(time())))

