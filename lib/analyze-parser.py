#!/usr/bin/env python

import os
import sys
import argparse
from glob import glob
from pprint import pformat
import numpy as np
import anylz

#  TODO this is messy wihtout using referenced stamps
#       --> add to config file

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
parser.add_argument("output_file",
    nargs="?",
    help="Full path of output file for writing analysis data"
)
parser.add_argument("-c", "--config",
    default="cfg/analyze.yml",
    help="Path to a configuration file"
)
parser.add_argument("-v", "--verbose",
    help="Output verbosity level"
)


if __name__ == "__main__":

    # First, handle arguments
    args = parser.parse_args()

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

    analyze_configuration = anylz.load_workflow_config(args.config)

    workflow_filename = analyze_configuration['workflow_filename']
    tasks_folder = analyze_configuration['tasks_folder']
    tasks_filenames = analyze_configuration['tasks_filenames']
    n_files_per_task = len(tasks_filenames)

    workload_timestamp_sequence = analyze_configuration['workload_sequence']
    task_timestamp_sequence = analyze_configuration['task_sequence']

    assert all([_is_globbable(tfnm) for tfnm in tasks_filenames])

    # Second, initialize data structures
    workflow_durations = list()
    tasks_durations = list()

    # Third, process the data
    for session_directory in session_directories:

        assert os.path.exists(os.path.join(session_directory, workflow_filename))

        tasks_files = list()

        for filename in tasks_filenames:
            tasks_files.append(sorted(glob(os.path.join(
                session_directory,
                tasks_folder,
                tasks_filename,
            ))))

        tasks_files = [single for multi in zip(*tasks_files) for single in multi]

        timestamps = anylz.roll_through_session(
            session_directory,
            workflow_filename,
            tasks_filename,
            workflow_timestamps,
        )

        # TODO aslso assert there is only 1 timestamp for things like start, stop
        assert len(timestamps['workflow']) == 1
        workflowstamps = timestamps['workflow'][0]
        taskstamps = timestamps['tasks']
        workflow_duration = anylz.timestamp_to_sinceepoch(
            workflowstamps[WorkflowStops][0]
        ) - anylz.timestamp_to_sinceepoch(
            workflowstamps[WorkflowStarts][0]
        )
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

