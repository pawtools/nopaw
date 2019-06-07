#!/usr/bin/env python

import sys
import os
from uuid import uuid1 as _uuid_
from time import time, sleep
from datetime import datetime
from pymongo import MongoClient, ReturnDocument



def get_task(collection, finder_id):
    locked_by_finder = {
        "executor": finder_id,
        "state"   : "pending",
    }

    locking_update = {"$set": locked_by_finder}

    created_task_filter = {
        "type" : "task",
        "state": "created",
    }

    task = collection.find_one_and_update(
        created_task_filter,
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

    thedata = """Jem says hello
    Jem says hi
    Every day Jemerson loves to try
    Things like reading, writing, climbing in a tree
    He's buzzing around like a bizzy bee
    bzzzzzzzzzzzzzzzzzzz
     - jem
    """

    my_id = _uuid_()

    mongodb = MongoClient(dbhost, dbport)
    db = mongodb[dbname]
    cl = db[dbname]

    my_task = get_task(cl, my_id)
    my_operation = my_task["operation"]

    # NOTE!! Different to_file Activity for reads vs writes
    if my_operation in ["read","write"]:
        to_file = my_task["to_file"]

        if to_file:
            my_datafile = "executors/executor.%s.data.out" % my_id

        else:
            thedata *= data_factor

    assert isinstance(my_task, dict)
    assert my_operation in {"read","write"}

    task_running_update = {"state":"running"}
    task_success_update = {"state":"success"}

    cl.update_one(
        {"_id"  : my_task["_id"]},
        {"$set": task_running_update},
    )

    if my_operation == "write":

        print("sync starting {}".format(
            datetime.fromtimestamp(time())))

        if to_file:
            sleeptime = 60./data_factor
            f_out = open(my_datafile, 'w')

            for _ in range(data_factor):
                f_out.write(thedata)
                sleep(sleeptime)

            f_out.close()

        else:
            cl.update_one(
                {"_id"  : my_task["_id"]},
                {"$set": {"data":thedata}},
            )
            sleep(60)

        print("sync stopping {}".format(
            datetime.fromtimestamp(time())))

    elif my_operation == "read":

        print("sync starting {}".format(
            datetime.fromtimestamp(time())))

        readdata = cl.find_one({"type":"data"})

        print("sync stopping {}".format(
            datetime.fromtimestamp(time())))

        print("going to verify at runtime...")

        if to_file:
            sleeptime = 60./data_factor
            f_out = open(my_datafile, 'w')

            for _ in range(data_factor):
                f_out.write(readdata["data"])
                sleep(sleeptime)

            f_out.close()

        else:
            sleep(60)

        if thedata == readdata['data']:
            print("Data was verified")

        else:
            print("This data was not verified: ")
            print("data lengths: expected %d, actual %d" %
                (len(thedata), len(readdata['data'])))

    cl.update_one(
        {"_id"  : my_task["_id"]},
        {"$set": task_success_update},
    )

    mongodb.close()

    print("pyscript stopping {}".format(
        datetime.fromtimestamp(time())))

