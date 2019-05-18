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
parser.add_argument("output_file",
    nargs="?",
    help="Full path of output file for writing analysis data"
)
parser.add_argument("-c", "--config",
    default="cfg/analyze.yml",
    help="Path to a configuration file"
)
parser.add_argument("-v", "--verbose",
    help="NotImplemented: Output verbosity level"
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

    with open(args.config, 'r') as f_config:
        #analyze_configuration = pawutils.load_config(args.config)
        analyze_configuration = yaml.safe_load(f_config)['analyze_workload']

    #workload_filenames = analyze_configuration['workload_filenames']
    workload_filename = analyze_configuration['workload_filenames'][0]
    tasks_folder       = analyze_configuration['tasks_folder']
    tasks_filenames    = analyze_configuration['tasks_filenames']
    workload_sequence  = analyze_configuration['workload_sequence']
    task_sequence      = analyze_configuration['task_sequence']

    n_files_per_task = len(tasks_filenames)
    timestamp_keys = {
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

  #  for session_directory in session_directories:
  #      # TODO aslso assert there is only 1 timestamp for things like start, stop
  #      assert len(timestamps['workflow']) == 1

  #      workflowstamps = timestamps['workflow'][0]
  #      taskstamps = timestamps['tasks']
  #      workflow_duration = anylz.timestamp_to_sinceepoch(
  #          workflowstamps[WorkflowStops][0]
  #      ) - anylz.timestamp_to_sinceepoch(
  #          workflowstamps[WorkflowStarts][0]
  #      )
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
