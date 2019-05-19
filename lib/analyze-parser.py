#!/usr/bin/env python

import os
import sys
import argparse
from glob import glob
from pprint import pformat
import numpy as np
import anylz
#import pawutils
import yaml

#  TODO this is messy wihtout using referenced stamps
#       --> add to config file
#  TODO ^^ after that ^^, give durations separate from
#       stamps
# TODO support multiple workload files
# TODO deal with missing files

_is_globbable = lambda x: x.find('*') >= 0

_data_format_template = (
    "{0: <7} {1: <12} {2: <12} {3: <12} "
    "{4: <12} {5: <12} {6: <12} {7: <12} "
    "{8: <12} {9: <12} {10: <12} {11: <12}"
)

parser = argparse.ArgumentParser(description="Analyze nopaw runs")
parser.add_argument("session_directories",
    help="Glob pattern or single directory to analyze"
)
parser.add_argument("output_timestamps",
    nargs="?", default="timestamps.txt",
    help="File name for writing analysis data (within each session)"
)
parser.add_argument("output_analysis",
    nargs="?", default="analysis.txt",
    help="File name for writing analysis data (within each session)"
)
parser.add_argument("output_profile",
    nargs="?", default="profile.txt",
    help="File name for writing profile data (within each session)"
)
parser.add_argument("-c", "--config",
    default="cfg/analyze.yml",
    help="Path to a configuration file"
)
parser.add_argument("-v", "--verbose",
    help="NotImplemented: Output verbosity level"
)

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

if __name__ == "__main__":

    # First, handle arguments
    args = parser.parse_args()

    print(args)
    print(sys.argv)

    if not _is_globbable(args.session_directories):
        # Looking to process MANY   directories
        session_directories = glob(args.session_directories)

    elif os.path.exists(args.session_directories):
        # Looking to process SINGLE directories
        session_directories = [args.session_directories]

    else:
        print("session_directories must be single folder or set of folders")
        print("(via glob pattern) containing data for analysis.")
        print("The given value '%s' does not meet the criteria" % 
            args.session_directories)
        print("Exiting")
        sys.exit(1)

    with open(args.config, 'r') as f_config:
        #analyze_configuration = pawutils.load_config(args.config)
        analyze_configuration = yaml.safe_load(f_config)['analyze_workload']

    #workload_filenames = analyze_configuration['workload_filenames']
    workload_filename   = analyze_configuration['workload_filenames'][0]
    tasks_folder        = analyze_configuration['tasks_folder']
    tasks_filenames     = analyze_configuration['tasks_filenames']
    workload_components = analyze_configuration['workload']
    task_components     = analyze_configuration['task']

    #workload_keys     = _unpack_stampkeys(workload_components)
    #task_keys         = _unpack_stampkeys(task_components)
    workload_sequence = _create_sequence(workload_components)
    task_sequence     = _create_sequence(task_components)

# TODO queryable object
#class timeline(object):
    workloadStart = workload_sequence[0]
    workloadStop  = workload_sequence[1]
    taskConnStart = task_sequence[0]
    taskConnStop  = task_sequence[-1]
    taskTaskStart = task_sequence[1]
    taskTaskStop  = task_sequence[-2]
    taskMainStart = task_sequence[2]
    taskMainStop  = task_sequence[-3]

    n_files_per_task = len(tasks_filenames)
    timestamp_keys = {
        #'workload': workload_keys,
        #'task': task_keys,
        'workload': workload_sequence,
        'task': task_sequence,
    }

    assert all([_is_globbable(tfnm) for tfnm in tasks_filenames])

    # Second, initialize data structures
    all_timestamps = dict()
    workload_durations = dict()
    tasks_durations = dict()

    # Third, process the data
    for session_directory in session_directories:

        all_timestamps[session_directory] = anylz.get_session_timestamps(
            session_directory,
            workload_filename,
            tasks_folder,
            tasks_filenames,
            timestamp_keys,
            convert_to_quantity=True,
        )

    durations = dict()
    analysis = dict()

    for session_directory, timestamps in all_timestamps.items():
        # TODO aslso assert there is only 1 timestamp for things like start, stop
        assert len(timestamps['workload']) == 1

        durations[session_directory] = durs = dict()
        analysis[session_directory] = anls = dict()

        durs['workload'] = workload_duration = list()
        durs['taskinit'] = taskinit_duration = list()
        durs['taskmain'] = taskmain_duration = list()
        durs['tasktask'] = tasktask_duration = list()
        durs['taskconn'] = taskconn_duration = list()
        durs['taskstop'] = taskstop_duration = list()

        workloadstamps = timestamps['workload'][0]
        workload_duration.append(workloadstamps[workloadStop][0] - workloadstamps[workloadStart][0])

        taskstamps = timestamps['task']
        for tks in taskstamps:
            taskinit_duration.append(tks[taskConnStart][0] - workloadstamps[workloadStart][0])
            taskstop_duration.append(workloadstamps[workloadStop][0] - tks[taskConnStop][0])
            taskmain_duration.append(tks[taskMainStop][0] - tks[taskMainStart][0])
            tasktask_duration.append(tks[taskTaskStop][0] - tks[taskTaskStart][0])
            taskconn_duration.append(tks[taskConnStop][0] - tks[taskConnStart][0])

        for interval,duration in durs.items():
            anls[interval] = (np.average(duration), np.std(duration))

        output_profile_path = os.path.join(session_directory, args.output_profile)
        output_analysis_path = os.path.join(session_directory, args.output_analysis)
        output_timestamps_path = os.path.join(session_directory, args.output_timestamps)

        with open(output_profile_path, 'w') as f_out:
            f_out.write(pformat(durs)+'\n')

        with open(output_analysis_path, 'w') as f_out:
            f_out.write(pformat(anls)+'\n')

        with open(output_timestamps_path, 'w') as f_out:
            f_out.write(pformat(timestamps)+'\n')

'''
        #print(pformat(taskstamps))
        workflow_durations.append( [nreplicates, workflow_duration] )
        # FILTER all tasks to get each different type
        # jsrun launched wrapper tasks
        wrappertasks = list(filter(lambda ts: all([ts.get(WrapperTaskStarts, None), ts.get(WrapperTaskStops, None)]), taskstamps))
        wrappertasks = list(filter(lambda ts: all([len(v) < 2 for v in ts.values()]), wrappertasks))
        # adaptivemd launched task instructions
        innertasks = list(filter(lambda ts: all([ts.get(InnerTaskStarts, None), ts.get(InnerTaskStops, None)]), taskstamps))
        innertasks = list(filter(lambda ts: all([len(v) < 2 for v in ts.values()]), innertasks))
        #print(pformat(wrappertasks))
        task_durations = list(map(
            lambda tts: anylz.timestamp_to_sinceepoch(tts[WrapperTaskStops][0]) - anylz.timestamp_to_sinceepoch(tts[WrapperTaskStarts][0]),
            wrappertasks))
        task_avgdur = np.mean(task_durations)
        task_stddur = np.std(task_durations)
        tasks_durations.append( [nreplicates, task_avgdur, task_stddur] )

print(_data_format_template.format("N Tasks", "W Dur", "T Dur,avg", "T Dur,std", "T Ini,avg", "T Ini,std", "T I,D,avg", "T I,D,std", "T I,I,avg", "T I,I,std", "T Clz,avg", "T Clz,std"))

'''
