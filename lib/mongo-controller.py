#!/usr/bin/env python

import sys
import os
from datetime import datetime
from time import time
from uuid import uuid1 as _uuid_
from pymongo import MongoClient


# FIXME paw "scripts" should import from pawtools!
#from pawtools import get_logger

print("pyscript recieved args:\n{}".format(
    sys.argv))

def runtime_check(check_func, interval=5, n_checks=0):
    for _ in n_checks:
        sleep(interval)
        yield check_func()


if __name__ == "__main__":

    dbhost = sys.argv[1]
    dbport = sys.argv[2]
    dbname = sys.argv[3]
    data_factor = sys.argv[4]

    if len(sys.argv) >= 7:

        nreplicates = sys.argv[5]
        task_operation = sys.argv[6]

        if len(sys.argv) == 8:
            # Treated as a flag
            to_file = sys.argv[7]
        else:
            to_file = False

    else:
        nreplicates = 0
        task_operation = False
        to_file = False

    assert nreplicates.find('.') < 0
    nreplicates = int(nreplicates)
    assert dbport.find('.') < 0
    dbport = int(dbport)
    assert data_factor.find('.') < 0
    data_factor = int(data_factor)

    thedata = """Jem says hello
    Jem says hi
    Every day Jemerson loves to try
    Things like reading, writing, climbing in a tree
    He's buzzing around like a bizzy bee
    bzzzzzzzzzzzzzzzzzzz
     - jem
    """ * data_factor

    # TODO known types (content class)
    document = {
        "_id" : _uuid_(),
        "data": thedata,
        "type": "data",
    }

    print("controller starting {}".format(
        datetime.fromtimestamp(time())))

    # Get connection to database
    mongodb = MongoClient(dbhost, dbport)
    db      = mongodb[dbname]
    cl      = db[dbname]

    # Creating data entry
    print("data synch starting {}".format(
        datetime.fromtimestamp(time())))

    cl.insert_one(document)

    print("data synch stopped {}".format(
        datetime.fromtimestamp(time())))

    # Creating Task entries for executors
    print("task synch starting {}".format(
        datetime.fromtimestamp(time())))

    for _ in range(nreplicates):
        cl.insert_one({
            "_id"      : _uuid_(),
            "type"     : "task",
            "operation": task_operation,
            "to_file"  : to_file,
            "state"    : "created",
            "heartbeat": 10,
            "data"     : None,
            "executor" : None,
        })

    print("task synch stopped {}".format(
        datetime.fromtimestamp(time())))

    if to_file:
        check_interval = 2
        n_checks = 10
        check_func = lambda: cl.find_many(
            {"state":"running"},
            {"proj" :"operation"},
        runtime_check(check_interval, n_checks)

    # Done with database
    mongodb.close()

    print("controller stopped {}".format(
        datetime.fromtimestamp(time())))
