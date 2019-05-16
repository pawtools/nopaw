'''
This module is for any timestamp processing utilities that
read files for timestamps, deal with timestamp values, or
collect the timestamps.
'''

import os
import datetime
_epoch = datetime.datetime.utcfromtimestamp(0)

import difflib
from functools import reduce

# TODO documentation!

def get_timestamp_values(filepath, keys):
    '''Get the timestamp values from a file

    Arguments
    ---------
    filepath ::
    path to file for parsing timestamps
    keys ::
    TODO 
    '''
    timestamps = {k: [] for k in keys}

    with open(filepath, 'r') as f:
        for line in f:
            ll = line.split()

            for k, stamps in timestamps.items():
                if line.find(k) >= 0:
                    stamp = ll[-1]

                    if len(ll) > 2 and len(ll[-2].split('-'))==3 \
                    and ll[-2].split('-')[0].startswith('2019'):
                        stamp = '_'.join([ll[-2], stamp])

                    stamps.append(stamp)

    return timestamps


def roll_through_session(session_directory, workflow_filename, tasks_filename, timestamp_keys):
    '''Process all matching task and workflow files
    from a **workload** execution session.
    Arguments
    ---------
    session_directory
    TODO 
    '''

    filenames = []

    _substr_from_match = lambda s,m: s[ m.a : m.a + m.size ]

    [    # Only 1 file should match!
     filenames.append(os.path.join(session_directory, d))
     if d.find(workflow_filename) >= 0 else None
     for d in os.listdir(session_directory)
    ]

    if isinstance(tasks_filename, list):
        filenames.extend(tasks_filename)
        # This gets largest common substring
        tasks_filename = reduce(
            lambda r,s: _substr_from_match(
                r, difflib.SequenceMatcher(
                    None, r, s).find_longest_match(
                    0, len(r), 0, len(s))),
            tasks_filename)

        assert len(tasks_filename) > 0

    else: 
        [
         filenames.append(os.path.join(session_directory, d))
         if d.find(tasks_filename) >= 0 else None
         for d in os.listdir(session_directory)
        ]

    workflow_timestamps = list()
    tasks_timestamps = list()

    timestamps = {
        "workflow": workflow_timestamps,
        "tasks":    tasks_timestamps,
    }

    for filename in filenames:
        filepath = os.path.abspath(filename)

        if filepath.find(workflow_filename) >= 0:
            workflow_timestamps.append(
                get_timestamp_values(filepath, timestamp_keys["workflow"]))

        if filepath.find(tasks_filename) >= 0:
            tasks_timestamps.append(
                get_timestamp_values(filepath, timestamp_keys["tasks"]))

    return timestamps


def timestamp_to_sinceepoch(timestamp, time_format=''):
    '''Convert timestamp to easily-compared value
    Here we just use time-since-epoch for quantifying all
    timestamp values
    '''
    # TODO support format given by argument
    possible_formats = [
        '%Y/%m/%d-%H:%M:%S.%f',
        '%Y-%m-%d_%H:%M:%S.%f',
    ]
    for _format in possible_formats:
        try:
            dt = datetime.datetime.strptime(timestamp, _format)
            break
        except ValueError:
            pass
    else:
        raise ValueError(
            "Could not process timestamp '%s' with available formats" %
            timestamp
        )

    return (dt - _epoch).total_seconds()

