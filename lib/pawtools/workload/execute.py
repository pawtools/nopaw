
import os
import yaml
from pprint import pformat

from .jobtools import JobBuilder, SessionMover#, MongoInstance
from ..logger import get_logger

# PAW Will use runtimes listed
# to import, 
__runtime__ = [
    "workload",
]

# TODO use these to navigate and build full runtime configuration
_required_configs = [
    "resource",  # description of node layout, queues, etc
    "sessions",  # prefix for all runtime session outputs
    "user",      # account information, ie allocation
    "workload",  # launch configuration
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
    task_config_filename = paw_config["tasks"].get(args.task_name, None)

    if not task_config_filename:
        raise Exception("No task configuration for given option: %s" % args.task_name)

    sessions_home = paw_home / paw_config["sessions"]
    task_config_location = paw_home / task_config_filename
    workload_config_location = paw_home / workload_config_filename
    shprofile = paw_home / args.pawrc

    session_mover = SessionMover(sessions_home)

    # Set all the needed options from config fields
    # Paw Runtime
    # Options commonly changed
    n_tasks = args.n_replicates
    job_name = args.job_name
    minutes = args.n_minutes
    # FIXME database/environment model not good
    db_location = args.db_location
    # TODO add these to options commonly changed config
    mpi_per_task = 1
    gpu_per_task = 1
    threads_per_task = 7
    threads_per_rank = 7

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
        gpu_per_task     = gpu_per_task,
        threads_per_task = threads_per_task,
        threads_per_rank = threads_per_rank,
    
        #Job and launcher Options
        # FIXME TODO move and replace source as appropriate
        allocation = 'bif112',
        minutes = minutes,
        n_nodes = 1,
    
        # TODO catch-all final options for task-specific
        #      should be processed here
        #Task Options
        mdsystem = "/gpfs/alpine/bif112/proj-shared/gromacs_systems/large-1M/md_RUNME.tpr",
        nsteps = 10000,
    )


    #  # Moves us to a new, unique subdirectory
    # TODO needs to capture env and do file linking
    #  session_mover.use_current()
    next_session_directory = session_mover.current
    os.mkdir(next_session_directory)
    os.chdir(next_session_directory)

    jb = JobBuilder()
    jb.load(workload_config_location)
    jb.load(task_config_location)

    # TODO this only makes sense for single workload
    #      applications, ie here every session gets own
    #      database, FIXME via expanded environment scheme
    jobconfig.update(dict(
        db_location = os.path.join(next_session_directory, db_location)
    ))
    jb.configure_workload(jobconfig)

    jb.launch_job()

    # Move logs that were left in first working
    # directory to the session's subdirectory
    #session_mover.go_back(capture=True)
