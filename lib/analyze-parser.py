#!/usr/bin/env python

import os
import sys

from glob import glob
from pprint import pformat

import numpy as np
import anylz

#if __name__ == "__main__":
#  TODO this is messy wihtout using referenced stamps
#  FIXME on all the retyped strings and come up with scheme for stamps

WorkflowStarts = "a worklow starts"
WorkflowStops  = "a worklow stops"
WrapperTaskStarts = "starts"
WrapperTaskStops  = "stops"
InnerTaskStarts = "starting"
InnerTaskStops  = "stopping"

if len(sys.argv) > 1:
    session_directories = glob(os.path.join(sys.argv[1], '*'))
else:
    session_directories = glob(os.path.join('weakscaling-rs42', '*'))

print("{0: <7} {1: <12} {2: <12} {3: <12} {4: <12} {5: <12} {6: <12} {7: <12} {8: <12} {9: <12} {10: <12} {11: <12}".format("N Tasks", "W Dur", "T Dur,avg", "T Dur,std", "T Ini,avg", "T Ini,std", "T I,D,avg", "T I,D,std", "T I,I,avg", "T I,I,std", "T Clz,avg", "T Clz,std"))

workflow_durations = list()
tasks_durations = list()
for session_directory in session_directories:
    if True:
    #if session_directory.endswith('weak-w-10'):
        nreplicates = int(session_directory.split('-')[-1])
    #print(session_directory)
    #try:
        #configfile = sys.argv[2]
     #   deep_session_directory = os.path.join(session_directory, 'sessions')
     #   deeper_session_directory = os.path.join(
     #       deep_session_directory,
     #       list(filter(lambda d: d.startswith('admd-0001.'),
     #                   os.listdir(deep_session_directory)))[0]
     #   )
     #   worker_logfile = os.path.join(deeper_session_directory, "adaptivemd.worker.*")
     #   workflow_filename = '-'.join(['pG', ''.join(session_directory.split('-'))])
     #   tasks_filename = glob(worker_logfile)
        workflow_filename = 'nopaw.out'
        assert os.path.exists(session_directory)
        assert os.path.exists(os.path.join(session_directory, workflow_filename))
        wrappers_filename = sorted(glob(os.path.join(session_directory, 'executors/nopaw.connector.*')))
        executors_filename = sorted(glob(os.path.join(session_directory, 'executors/nopaw.executor.*')))
        tasks_filename = [single for pair in zip(wrappers_filename, executors_filename) for single in pair]
        workflow_timestamps = {
            "workflow": {WorkflowStarts, WorkflowStops},
            "tasks"    : {WrapperTaskStarts, WrapperTaskStops, InnerTaskStarts, InnerTaskStops},
        }
        #print(wrappers_filename)
        #print(executors_filename)
        #print(workflow_timestamps)
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

