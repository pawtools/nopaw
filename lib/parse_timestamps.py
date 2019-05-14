#!/usr/bin/env python

import sys
import os
import numpy as np

from glob import glob
from pprint import pformat

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
for session_directory in session_directories:
    if session_directory.endswith('weak-w-10'):
    #print(session_directory)
    #try:
    #if True:
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
        #print(len(timestamps['tasks']))
        #continue
        # TODO aslso assert there is only 1 timestamp for things like start, stop
        assert len(timestamps['workflow']) == 1
        workflowstamps = timestamps['workflow'][0]
        taskstamps = timestamps['tasks']
        workflow_duration = timestamp_to_sinceepoch(
            workflowstamps[WorkflowStops][0]
        ) - timestamp_to_sinceepoch(
            workflowstamps[WorkflowStarts][0]
        )
        #print(pformat(taskstamps))
        # FILTER all tasks to get each different type
        # jsrun launched wrapper tasks
        wrappertasks = list(filter(lambda ts: all([ts.get(TaskStarts, None), ts.get(TaskStops, None)]), taskstamps))
        wrappertasks = list(filter(lambda ts: all([len(v) < 2 for v in ts.values()]), wrappertasks))
        # adaptivemd launched task instructions
        innertasks = list(filter(lambda ts: all([ts.get(AmdTaskStarts, None), ts.get(AmdTaskStops, None)]), taskstamps))
        innertasks = list(filter(lambda ts: all([len(v) < 2 for v in ts.values()]), innertasks))
        #print(pformat(wrappertasks))
        task_durations = list(map(
            lambda tts: timestamp_to_sinceepoch(tts[TaskStops][0]) - timestamp_to_sinceepoch(tts[TaskStarts][0]),
            wrappertasks))
        task_avgdur = np.mean(task_durations)
        task_stddur = np.std(task_durations)
        #print(task_avgdur)
        #print(task_stddur)
        itask_durations = list(map(
            lambda tts: timestamp_to_sinceepoch(tts[AmdTaskStops][0]) - timestamp_to_sinceepoch(tts[AmdTaskStarts][0]),
            innertasks))
        itask_avgdur = np.mean(itask_durations)
        itask_stddur = np.std(itask_durations)
        #print(itask_avgdur)
        #print(itask_stddur)
        itask_inis = list(map(lambda tts: timestamp_to_sinceepoch(tts[AmdTaskStarts][0]) - timestamp_to_sinceepoch(workflowstamps[WorkflowStarts][0]), innertasks))
        itask_avgini = np.mean(itask_inis)
        itask_stdini = np.std(itask_inis)
        task_inis = list(map(lambda tts: timestamp_to_sinceepoch(tts[TaskStarts][0]) - timestamp_to_sinceepoch(workflowstamps[WorkflowStarts][0]), wrappertasks))
        task_avgini = np.mean(task_inis)
        task_stdini = np.std(task_inis)
        task_clzs = list(map(lambda tts: timestamp_to_sinceepoch(workflowstamps[WorkflowStops][0]) - timestamp_to_sinceepoch(tts[TaskStops][0]), wrappertasks))
        task_avgclz = np.mean(task_clzs)
        task_stdclz = np.std(task_clzs)
        n_tasks = len(timestamps['tasks'])
        print("{0: <7} {1: 12.4f} {2: 12.4f} {3: 12.4f} {4: 12.4f} {5: 12.4f} {6: 12.4f} {7: 12.4f} {8: 12.4f} {9: 12.4f} {10: 12.4f} {11: 12.4f}".format(n_tasks, workflow_duration, task_avgdur, task_stddur, task_avgini, task_stdini, itask_avgdur, itask_stddur, itask_avgini, itask_stdini, task_avgclz, task_stdclz))
    #    except Exception as e:
    #        print("ERRORED while looking in {}".format(session_directory))
    #        print(len(tasks_filename))
    #        print("Skipping 1, got error")
    #        print(e)
