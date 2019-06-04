
import os
import yaml
from pprint import pformat

from .jobtools import JobBuilder, SessionMover#, MongoInstance
from ..logger import get_logger


def process_data_factor(data_multiply):

    data_multiply = data_multiply.lower()

    if data_multiply.endswith('k'):
        _factor = 1000
    elif data_multiply.endswith('m'):
        _factor = 1000000
    elif data_multiply.endswith('g'):
        _factor = 1000000000
    else:
        _factor = 1

    return int(data_multiply[:-1]) * _factor


# PAW Will use runtimes listed
# to import, 
__runtime__ = [
    "workload",
]

# TODO use these to navigate and build full runtime configuration
_required_configs = [
    "resource",  # description of node layout, queues, etc
    "user",      # account information, ie allocation
    "workload",  # job configuration
    "launcher",    # launch configuration
    "executor",  # wrapper configuration
]

def workload(args, paw_home):

    # FIXME the loglevel input broken right now
    logger = get_logger(__name__, "INFO" if args.verbose else "WARNING")
    #logger = pawtools.get_logger(__name__, "INFO")
    logger.setLevel("INFO" if args.verbose else "WARNING")
    logger.critical("LOGLEVEL set to: {}".format(logger.level))
    logger.info("Running PAW command '%s'"%args.command)
    logger.info("with args {}".format(args))

    paw_config_location = paw_home / args.config
    # FIXME FIXME
    # TODO need a persistent, accumulating config
    # TODO where should it be built? top, here?
    with open(paw_config_location, 'r') as f_config:
        paw_config = yaml.safe_load(f_config)

    workload_config_filename = paw_config["workload"]
    launcher_config_filename = paw_config["launcher"]
    executor_config_filename = paw_config["executor"].get(args.executor, None)
    if not executor_config_filename:
        raise Exception("No task configuration for given option: %s" % args.executor)
    executor_config_location = paw_home / executor_config_filename
    launcher_config_location = paw_home / launcher_config_filename
    workload_config_location = paw_home / workload_config_filename

    shprofile = paw_home / args.pawrc
    session_home  = paw_home / args.session_home
    session_name  = args.session_name
    session_mover = SessionMover(session_home, session_name)

    # TODO get from config
    cores_per_node = 42
    gpu_per_node = 6
    allocation = "bif112"
    data_factor = 1

    # Set all the needed options from config fields
    # Paw Runtime
    # Options commonly changed
    if len(args.task_args) not in (1,2):
        raise Exception("Require argument 'operation' for option '-t'/'--task_args'")

    else:
        operation = args.task_args[0]

        if len(args.task_args) == 2:
            data_factor = process_data_factor(args.task_args[1])

    n_tasks = args.n_replicates
    job_name = args.job_name
    minutes = args.n_minutes
    # FIXME database/environment model not good
    n_mongo_nodes = 1
    db_location = args.db_location
    # TODO add these to options commonly changed config
    mpi_per_task = 1
    #gpu_per_task = 0
    threads_per_task = 1
    threads_per_rank = 1
    n_nodes = int(args.n_replicates)//int(cores_per_node) + bool(int(args.n_replicates)%int(cores_per_node)) + int(n_mongo_nodes)

    # Task here is like "MD task" of whatever
    # is assigned to a single MD instance.
    #
    # On Summit, this maps to "resource set"
    # for non-MPI tasks
    # TODO TODO list missing config fields
    #      somewhere downstream from here
    jobconfig = dict(
        n_tasks          = n_tasks,
        job_name         = job_name,
        shprofile        = shprofile,
        mpi_per_task     = mpi_per_task,
        #gpu_per_task     = gpu_per_task,
        threads_per_task = threads_per_task,
        threads_per_rank = threads_per_rank,
    
        #Job and launcher Options
        # FIXME TODO move and replace source as appropriate
        allocation = allocation,
        minutes = minutes,
        n_nodes = n_nodes,
    
        # TODO catch-all final options for task-specific
        #      should be processed here
        #Task Options
        operation        = operation,
        data_factor      = data_factor,
    )

    logger.info(pformat(jobconfig))

    #  # Moves us to a new, unique subdirectory
    # TODO needs to capture env and do file linking
    #  session_mover.use_current()
    next_session_directory = session_mover.current
    os.mkdir(next_session_directory)
    os.chdir(next_session_directory)

    jb = JobBuilder()
    jb.load(workload_config_location)
    jb.load(executor_config_location)
    jb.load(launcher_config_location)

    # TODO this only makes sense for single workload
    #      applications, ie here every session gets own
    #      database, FIXME via expanded environment scheme
    jobconfig.update(dict(
        db_location = os.path.join(next_session_directory, db_location)
    ))
    jb.configure_workload(jobconfig)
    logger.info(pformat(jb.job_configuration))

    jb.launch_job()

    # Move logs that were left in first working
    # directory to the session's subdirectory
    #session_mover.go_back(capture=True)
