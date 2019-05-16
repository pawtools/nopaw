#!/usr/bin/env python

import sys
import os
from pprint import pformat
from pymongo import MongoClient


print("verify script recieved args:\n{}".format(
    sys.argv))

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

    verify_filename = os.path.join("sessions", runname, "verify-data.pyd")
    verified = os.path.join("sessions", runname, "verified.true")
    notverified = os.path.join("sessions", runname, "verified.false")

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

    mongodb = MongoClient(dbhost, dbport)

    db = mongodb[dbname]
    cl = db[dbname]

    verify_data = dict()
    verify_data["count"] = count = 0
    verify_data["correct"] = correct = list()
    verify_data["wrong"] = wrong = list()

    if operation == "read":
        raise NotImplemented

    elif operation == "write":
        for document in cl.find():
            count += 1
            if thedata == document["data"]:
                correct.append(document["_id"])
            else:
                wrong.append(document["_id"])
                print("this data was 'wrong':")
                print(document["data"])

        # database is always primed with
        # data using for the read operation
        if len(verify_data["wrong"]) == 0:
            if len(verify_data["correct"]) == 1 + nreplicates:
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


    with open(verify_filename, 'w') as f_verify:
        f_verify.write(pformat(verify_data))

