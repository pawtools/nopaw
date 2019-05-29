
import os
import itertools

from .jobtools import JobBuilder, SessionMover#, MongoInstance


# PAW Will use runtimes listed
# to import, 
__runtime__ = [
    "workload",
]

def workload(args, config_filepath):

    fwd = os.getcwd()
    session_mover = SessionMover(fwd)

    # Set all the needed options from config fields
    # Paw Runtime
    shprofile = args.pawrc
    # Options commonly changed
    n_tasks = args.n_replicates
    job_name = args.job_name
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
        allocation = 'bif112',
        minutes = 10,
        n_nodes = 1,
        rcfile = "/gpfs/alpine/bif112/proj-shared/tests-summit/tests-gromacs/testrc.bash",
    
        #Task Options
        mdsystem = "/gpfs/alpine/bif112/proj-shared/gromacs_systems/large-1M/md_RUNME.tpr",
        nsteps = 10000,
    )


    #  # Moves us to a new, unique subdirectory
    # TODO needs to capture env and do file linking
    #  session_mover.use_current()

    jb = JobBuilder()
    jb.load(config_filepath)
    jb.configure_workload(jobconfig)

    next_session_directory = session_mover.current
    os.mkdir(next_session_directory)
    os.chdir(next_session_directory)

    jb.launch_job()

    # Move logs that were left in first working
    # directory to the session's subdirectory
    session_mover.go_back(capture=True)
