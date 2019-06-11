#!/usr/bin/env python

import sys
import os
import subprocess
from pprint import pformat
from datetime import datetime
from time import time, sleep
from uuid import uuid1 as _uuid_
from pymongo import MongoClient


def check_directory_contents(directory="executors"):
    process = subprocess.Popen(['ls', '-grt', directory], stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out, err


# FIXME paw "scripts" should import from pawtools!
#from pawtools import get_logger

print("pyscript recieved args:\n{}".format(
    sys.argv), flush=True)

do_signal = 0

def check_executors_alive(collection, heartbeat=10, f_out=None, wait_beats=3):

    print("check function arguments: ", flush=True)
    print(collection, heartbeat, wait_beats, f_out, flush=True)

    waitstart = 35
    timestart = time()

    def _check_executors_alive(collection, heartbeat, f_out, waitstart, timestart):
        now   = int(time())
        print("Performing a check now %s" % datetime.fromtimestamp(now), flush=True)
        tasks = [ta for ta in collection.find({"type":"task"}, projection=["state","executor","signal","lastseen"])]

        if f_out:
            f_out.write('%s\n' % datetime.fromtimestamp(now))
            f_out.write('%s\n' % pformat(tasks))
            f_out.flush()

        if do_signal:
            if now - timestart > 40 and now - timestart < 40 + heartbeat + 1:
                print("Emitting Signal", flush=True)
                #collection.update_many({"type":"task"}, {"$set":{"signal":"pause 15"}})
                collection.update_many({"type":"task"}, {"$set":{"signal":"restart"}})
                do_signal -= 1

        #print(pformat(tasks), flush=True)
        #print([now - ta["lastseen"] for ta in tasks], flush=True)
        #print([now - ta["lastseen"] < wait_beats * heartbeat for ta in tasks], flush=True)
        #print([ta["state"] == "created" for ta in tasks], flush=True)
        return any([
            (
             ((   now - timestart      < waitstart             ) and (ta["state"] == "created"))
             or ((now - ta["lastseen"] < wait_beats * heartbeat) and (ta["state"] == "running"))
             or ((now - ta["lastseen"] < wait_beats * heartbeat) and (ta["state"] == "success"))
            )
            for ta in tasks
        ])

    return lambda: _check_executors_alive(collection, heartbeat, f_out, waitstart, timestart)


check_executor_files = lambda : '\n{} filelist:\n'.format(
    datetime.fromtimestamp(time())) \
    + '\n'.join([str(c, 'utf-8') for c in check_directory_contents() if c is not None])


def runtime_check(check_func, interval=5, n_checks=None):
    """Blocking function
    """
    print("Runtime checks will be done with this function", flush=True)
    print(check_func, flush=True)
    if n_checks:
        raise NotImplementedError

    while check_func():
        sleep(interval)


if __name__ == "__main__":

    dbhost = sys.argv[1]
    dbport = sys.argv[2]
    dbname = sys.argv[3]
    data_factor = sys.argv[4]
    heartbeat = 5

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
        datetime.fromtimestamp(time())), flush=True)

    # Get connection to database
    mongodb = MongoClient(dbhost, dbport)
    db      = mongodb[dbname]
    cl      = db[dbname]

    # Creating data entry
    print("data synch starting {}".format(
        datetime.fromtimestamp(time())), flush=True)

    cl.insert_one(document)

    print("data synch stopped {}".format(
        datetime.fromtimestamp(time())), flush=True)

    # Creating Task entries for executors
    print("task synch starting {}".format(
        datetime.fromtimestamp(time())), flush=True)

    for _ in range(nreplicates):
        cl.insert_one({
            "_id"      : _uuid_(),
            "type"     : "task",
            "operation": task_operation,
            "to_file"  : to_file,
            "state"    : "created",
            "heartbeat": heartbeat,
            "lastseen" : 0,
            "signal"   : None,
            "data"     : None,
            "executor" : None,
        })

    print("task synch stopped {}".format(
        datetime.fromtimestamp(time())), flush=True)

    if to_file or task_operation == "hello":
        f_out = open("controller.result.out", "w")

        runtime_check(
            check_executors_alive(cl, heartbeat, f_out),
            heartbeat,
        )
        f_out.close()

    # Done with database
    mongodb.close()

    print("controller stopped {}".format(
        datetime.fromtimestamp(time())), flush=True)
