#!/usr/bin/env python

import os
import sys
import yaml
from glob import glob
from pprint import pformat
import numpy as np

from pawtools.timestamp import get_session_timestamps
from pawtools.logger import get_logger

__runtime__ = [
    "analyze",
]

# TODO TODO TODO read the files and restore data structres
#                to make later plotting super easy!

#  TODO add stamp references to config file
#       --> 
#  TODO ^^ after that ^^, give durations separate from
#       stamps
# TODO support multiple workload files
# TODO deal with missing files

#> KEEP# # TESTS! yay!
#> KEEP# nested_dict = dict(
#> KEEP#     a={1,2,3},
#> KEEP#     b="5",
#> KEEP#     c=dict(b=10, bbb=dict(butt="6006"))
#> KEEP# )
#> KEEP# flatten_nested_dict(nested_dict)
def flatten_nested_dict(d):
    new = dict()
    assert isinstance(d, dict)
    for k,v in d.items():
        if isinstance(v, dict):
            if k in new:
                print("WARNING: value for existing key {} being overwritten")
            new.update(flatten_nested_dict(v))
        else:
            new.update({k:v})
    return new

def collect_XY_columns(data, key):
    assert isinstance(data, dict)

    X = sorted(data)
    Y = [data[x][key] for x in X]

    return np.array(X, Y)


_is_globbable = lambda x: x.find('*') >= 0

#_unpack_stampkeys = lambda x: [s for c in x.values() for s in c]
# assumes the given order and strict embedding
#_create_sequence  = lambda y: list([single for multi in zip(*[s for x in y for s in x.values()]) for single in multi])
_create_sequence  = lambda y: [
    single for multi in [
        f if i==0 else list(reversed(f))
        for i,f in enumerate(zip(
        *[s for x in y for s in x.values()]))
    ]
    for single in multi
]


def analyze(args, config_filepath):
    logger = get_logger(__name__, "INFO" if args.verbose else "WARNING")
    # FIXME the level input broken right now
    logger = get_logger(__name__, "INFO" if args.verbose else "WARNING")
    #logger = pawtools.get_logger(__name__, "INFO")
    logger.setLevel("INFO" if args.verbose else "WARNING")
    logger.critical("LOGLEVEL set to: {}".format(logger.level))

    #-----------------------------------------------------------#
    # Second thing first, read and set configuration
    logger.info("Reading config from file: %s"%config_filepath)

    with open(config_filepath, 'r') as f_config:
        #analyze_configuration = pawutils.load_config(args.config)
        analyze_configuration = yaml.safe_load(f_config)

    #workload_filenames = analyze_configuration['workload_filenames']
    #del#workload_folder     = analyze_configuration['workload']['folder']
    workload_filename   = analyze_configuration['workload']['filenames'][0]
    workload_components = analyze_configuration['workload']['timestamps']

    tasks_filenames     = analyze_configuration['task']['filenames']
    tasks_folder        = analyze_configuration['task']['folder']
    task_components     = analyze_configuration['task']['timestamps']

    #workload_keys     = _unpack_stampkeys(workload_components)
    #task_keys         = _unpack_stampkeys(task_components)
    workload_sequence = _create_sequence(workload_components)
    task_sequence     = _create_sequence(task_components)

    #-----------------------------------------------------------#
    # First thing second, handle arguments (use config a bit)
    if os.path.isfile(os.path.join(args.session_directory, workload_filename)):
        # Looking to process SINGLE directories
        session_directories = [args.session_directory]

    elif os.path.isdir(args.session_directory):
        # Looking to process MANY   directories
        session_directories = list()
        for d in os.listdir(args.session_directory):
            if os.path.isfile(os.path.join(args.session_directory, d, workload_filename)):
                session_directories.append(os.path.join(args.session_directory, d))

        if len(session_directories) == 0:
            logger.info("session_directories must be single folder or top of")
            logger.info("a set of folders containing data for analysis.")
            logger.info("The given value '%s' does not lead to any folders" % 
                args.session_directory)
            logger.info("or subfolders with the workflow file '%s' specified" %
                workflow_filename)
            logger.info("by the configuration, Exiting")
            sys.exit(1)

    else:
        logger.info("session_directories must be single folder or top of")
        logger.info("a set of folders containing data for analysis.")
        logger.info("The given value '%s' does not meet the criteria" % 
            args.session_directory)
        logger.info("Exiting")
        sys.exit(1)

    #-----------------------------------------------------------#
    # Second thing again, configuring processing setup
# TODO queryable object
#class timeline(object):
    # TODO incorporate all this into config file
    workloadStart = workload_sequence[0]
    workloadStop  = workload_sequence[1]
    taskConnStart = task_sequence[0]
    taskConnStop  = task_sequence[-1]
    taskTaskStart = task_sequence[1]
    taskTaskStop  = task_sequence[-2]
    taskMainStart = task_sequence[2]
    taskMainStop  = task_sequence[-3]
    interval_timestamp_keys = dict()
    interval_timestamp_keys['workload'] = workload = [workloadStart, workloadStop]
    interval_timestamp_keys['taskinit'] = taskinit = [workloadStart, taskConnStart]
    interval_timestamp_keys['taskstop'] = taskstop = [taskConnStop, workloadStop]
    interval_timestamp_keys['taskmain'] = taskmain = [taskMainStart, taskMainStop]
    interval_timestamp_keys['tasktask'] = tasktask = [taskTaskStart, taskTaskStop]
    interval_timestamp_keys['taskconn'] = taskconn = [taskConnStart, taskConnStop]
    interval_timestamp_keys['taskboot'] = taskboot = [taskConnStart, taskTaskStart]
    interval_timestamp_keys['taskpre']  = taskpre  = [taskTaskStart, taskMainStart]
    interval_timestamp_keys['taskpost'] = taskpost = [taskMainStop, taskTaskStop]
    interval_timestamp_keys['taskend']  = taskpost = [taskTaskStop, taskConnStop]
    interval_plotlabel_keys = dict()
    interval_plotlabel_keys['workload'] = "Wtotal"
    interval_plotlabel_keys['taskinit'] = "Einit"
    interval_plotlabel_keys['taskstop'] = "Eclose"
    interval_plotlabel_keys['taskmain'] = "Tmain"
    interval_plotlabel_keys['tasktask'] = "Ttotal"
    interval_plotlabel_keys['taskconn'] = "Elive"
    interval_plotlabel_keys['taskboot'] = "Tboot"
    interval_plotlabel_keys['taskpre']  = "Tpre"
    interval_plotlabel_keys['taskpost'] = "Tpost"
    interval_plotlabel_keys['taskend']  = "Edisconnect"

    n_files_per_task = len(tasks_filenames)

    timestamp_keys = {
        'workload': workload_sequence,
        'task': task_sequence,
    }

    assert all([_is_globbable(tfnm) for tfnm in tasks_filenames])

    #-----------------------------------------------------------#
    # Third, initialize data structures
    all_timestamps = dict()
    durations = dict()
    analysis = dict()

    #-----------------------------------------------------------#
    # Fourth, read in the workload profile data
    for session_directory in session_directories:

        all_timestamps[session_directory] = get_session_timestamps(
            session_directory,
            workload_filename,
            tasks_folder,
            tasks_filenames,
            timestamp_keys,
            convert_to_quantity=True,
        )

    logger.info("All Timestamps:\n{}".format(pformat(all_timestamps)))

    #-----------------------------------------------------------#
    # Fifth, calculate execution durations
    for session_directory, timestamps in all_timestamps.items():
        # TODO aslso assert there is only 1 timestamp
        #      for things like start, stop
        assert len(timestamps['workload']) == 1

        durations[session_directory] = durs = dict()
        [
         durs.update({interval:list()})
         for interval in interval_timestamp_keys
        ]

        for taskstamps in timestamps['task']:
            _stamps = {
                k:v for k,v in timestamps['workload'][0].items()
            }
            _stamps.update(taskstamps)
            for key, (start, stop) in interval_timestamp_keys.items():
                durs[key].append(
                    _stamps[stop][0] - _stamps[start][0])

    #-----------------------------------------------------------#
    # Sixth, calculate duration statistics
    for session_directory, durs in durations.items():
        analysis[session_directory] = anls = dict()

        for interval,duration in durs.items():
            anls[interval] = (np.average(duration), np.std(duration))

    #-----------------------------------------------------------#
    # Seventh, save the analysis
    for session_directory in session_directories:

        durs = durations[session_directory]
        anls = analysis[session_directory]

        timestamps = all_timestamps[session_directory]

        output_profile_path = os.path.join(
            session_directory, args.output_profile)

        output_analysis_path = os.path.join(
            session_directory, args.output_analysis)

        output_timestamps_path = os.path.join(
            session_directory, args.output_timestamps)

        with open(output_profile_path, 'w') as f_out:
            f_out.write(pformat(durs)+'\n')

        with open(output_analysis_path, 'w') as f_out:
            f_out.write(pformat(anls)+'\n')

        with open(output_timestamps_path, 'w') as f_out:
            f_out.write(pformat(timestamps)+'\n')

    if args.plot:

        #--------------------------------------------------------#
        # PLOT 1: Weak Scaling Plot- Workload Total
        from pawtools.plots import plot_weak_scaling

        n_replicates, w_total = list(), list()
        plot_filepath = '-'.join([args.plot.strip("/"), "weak-scaling.png"])

        logger.info("plotting here: %s" % plot_filepath)

        for session_directory in session_directories:
            # FIXME clearly need better way to specify n replicates
            #       --> read from workflow file above,
            #           tracking errors and such as well
            n_replicates.append(len(durations[session_directory]["taskmain"]))
            w_total.append(analysis[session_directory]["workload"][0])

        n_replicates, w_total = list(zip(*list(sorted(
            zip(n_replicates, w_total),
            key=lambda x: x[0]
        ))))

        logger.info(
            "Plotting Weak Scaling results:\nN Replicates: {0}\nW Duration: {1}".format(
            n_replicates, w_total)
        )

        plot_weak_scaling.makeplot(n_replicates, w_total, plot_filepath)
        # TODO MORE PLOTS!

