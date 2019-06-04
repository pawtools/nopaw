#!/usr/bin/env python

import os
import yaml
from pprint import pformat
from pymongo import MongoClient

from .logger import get_logger
from .workload.jobtools import MongoInstance
from .workload.execute import process_data_factor

# TODO use the jobtools.MongoInstance to launch

__runtime__ = [
    "verify",
]

def verify(args, paw_home):

    logger = get_logger(__name__, "INFO" if args.verbose else "WARNING")
    #logger = pawtools.get_logger(__name__, "INFO")
    logger.setLevel("INFO" if args.verbose else "WARNING")
    logger.critical("LOGLEVEL set to: {}".format(logger.level))
    logger.info("Running PAW command '%s'"%args.command)
    logger.info("with args {}".format(args))

    paw_config_location = paw_home / args.config

    # Set all the needed options from config fields
    # Paw Runtime
    # Options commonly changed
    if not isinstance(args.task_args, list):
        raise Exception("Option '-t'/'--task_args' must be given")
    elif len(args.task_args) not in (1,2):
        raise Exception("Require argument 'operation' for option '-t'/'--task_args'")
    else:
        operation = args.task_args[0]

        if len(args.task_args) == 2:
            data_factor = process_data_factor(args.task_args[1])

    session_directory = args.session_directory
    nreplicates = args.n_replicates
    dbhost      = args.db_host
    dbport      = args.db_port
    dbname      = args.db_name
    dbpath      = args.db_location
    dblocation  = paw_home / session_directory / dbpath

    verified = os.path.join(session_directory, "verified.true")
    notverified = os.path.join(session_directory, "verified.false")
    verify_filename = os.path.join(session_directory, "verify-data.pyd")

    thedata = """Jem says hello
    Jem says hi
    Every day Jemerson loves to try
    Things like reading, writing, climbing in a tree
    He's buzzing around like a bizzy bee
    bzzzzzzzzzzzzzzzzzzz
     - jem
    """ * data_factor

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
                if line.strip().find(verified_message) >= 0:
                    count += 1
                    correct.append(executor)
                    break
            else:
                wrong.append(executor)

    elif operation == "write":
        # FIXME NOTE we (hopefully) harmlessly opening
        #            and closing the DB
        mongo = MongoInstance(dblocation)
        mongo.open_mongodb()
        # and open client to it
        mongodb = MongoClient(dbhost, dbport)
        db = mongodb[dbname]
        cl = db[dbname]

        # NOTE writes are verified here and now
        for document in cl.find():
            count += 1
            if thedata == document["data"]:
                correct.append(document["_id"])
            else:
                wrong.append(document["_id"])
                print("this data was 'wrong':")
                print(document["data"])

        mongo.stop_mongodb()
        mongodb.close()

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

