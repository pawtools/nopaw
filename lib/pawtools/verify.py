#!/usr/bin/env python

import sys
import os
from pprint import pformat
from pymongo import MongoClient

__all__ = [
    "verifier",
]

def verifier():
    pass

if __name__ == "__main__":

    if sys.argv[0]:
        dbhost = sys.argv[1]
        dbport = sys.argv[2]
        dbname = sys.argv[3]
        runname = sys.argv[4]
        operation = sys.argv[5]
        nreplicates = sys.argv[6]

    else:
        dbhost = "0.0.0.0"
        dbport = "27017"
        dbname = "testdb"
        runname = "write10"
        operation = "write"
        nreplicates = "10"

    session_directory = os.path.join("sessions", runname)

    verified = os.path.join(session_directory, "verified.true")
    notverified = os.path.join(session_directory, "verified.false")
    verify_filename = os.path.join(session_directory, "verify-data.pyd")

    assert dbport.find('.') < 0
    assert nreplicates.find('.') < 0
    dbport = int(dbport)
    nreplicates = int(nreplicates)

    thedata = """Jem says hello
    Jem says hi
    Every day Jemerson loves to try
    Things like reading, writing, climbing in a tree
    He's buzzing around like a bizzy bee
    bzzzzzzzzzzzzzzzzzzz
     - jem
    """

    # FIXME NOTE we (hopefully) harmlessly opening
    #            and closing the DB even for read
    #            verify where its not used
    mongodb = MongoClient(dbhost, dbport)

    db = mongodb[dbname]
    cl = db[dbname]

    verify_data = dict()
    verify_data["correct"] = correct = list()
    verify_data["wrong"] = wrong = list()

    count = 0

    if operation == "read":
        # NOTE this is not an independent verifitcation
        #      - the task knows what the data was and
        #        checked it on the fly, no other way to
        #        allow later verification without adding
        #        additional task operations
        verified_message = "Data was verified"
        executors_prefix = os.path.join(session_directory, 'executors')
        executor_filename = "nopaw.executor."
        executors = map(
            lambda ffnm: os.path.join(executors_prefix, ffnm),
            filter(lambda fnm: fnm.find(executor_filename) >= 0,
                os.listdir(executors_prefix)
            )
        )

        for executor in executors:
            for line in open(executor, 'r').readlines():
                if line.strip() == verified_message:
                    count += 1
                    correct.append(executor)
                    break
            else:
                wrong.append(executor)

    elif operation == "write":
        # NOTE writes are verified here and now
        for document in cl.find():
            count += 1
            if thedata == document["data"]:
                correct.append(document["_id"])
            else:
                wrong.append(document["_id"])
                print("this data was 'wrong':")
                print(document["data"])


    if len(verify_data["wrong"]) == 0:
        # database is always primed with
        # data using for the read operation
        # so... the write verify method above
        #       counts an extra entry, just
        #       letting it fly for now
        if operation == "write" and len(verify_data["correct"]) == 1 + nreplicates \
        or operation == "read" and len(verify_data["correct"]) == nreplicates:
            print("All {0}/{1} replicates verified".format(
                len(verify_data["correct"]), nreplicates))

            open(verified, 'w').close()

        else:
            print("None wrong, but only have data")
            print("for {0}/{1} replicates".format(
                len(verify_data["correct"]), nreplicates))

            open(notverified, 'w').close()

    else:
        print("{0}/{1} replicates had incorrect data".format(
            len(verify_data["wrong"]), nreplicates))

        open(notverified, 'w').close()


    verify_data["count"] = count
    with open(verify_filename, 'w') as f_verify:
        f_verify.write(pformat(verify_data))

