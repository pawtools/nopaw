'''
This module is for any timestamp processing utilities that
read files for timestamps, deal with timestamp values, or
collect the timestamps.
'''

import os
from glob import glob
import datetime
_epoch = datetime.datetime.utcfromtimestamp(0)

#del#import difflib
#del#from functools import reduce

__all__ = [
    "get_session_timestamps",
]

# TODO documentation!

def get_session_timestamps(
        session_directory, workload_filename, tasks_folder, tasks_filenames,
        timestamp_keys, convert_to_quantity=False, timestamp_reference=None):

    # TODO use timestamp reference to select a single
    #      zero point for the workload/session

    workload_file = os.path.join(session_directory, workload_filename)
    tasks_files = list()

    assert os.path.exists(workload_file)

    for filename in tasks_filenames:
        tasks_files.append(sorted(glob(os.path.join(
            session_directory,
            tasks_folder,
            filename,
        ))))

    # FIXME
    # both flat/grouped cases fail
    # if any file is missing
    tasks_files = [
        multi for multi in zip(*tasks_files)
    #    single for multi in zip(*tasks_files)
    #    for single in multi
    ]

    # FIXME simple for now but this is not very good,
    #      --->  what if files are missing?
    n_replicates = len(tasks_files)
    #n_replicates = len(tasks_files) / n_files_per_task

    #print(tasks_files)
    #print(n_replicates)

    timestamps = roll_through_session(
        session_directory,
        workload_file,
        tasks_files,
        timestamp_keys,
        convert_to_quantity,
    )

    return timestamps


def get_timestamp_values(filepath, keys, convert_to_quantity=False):
    '''Get the timestamp values from a file

    Arguments
    ---------
    filepath ::
    path to file for parsing timestamps
    keys ::
    TODO 
    '''
    # TODO remove nonempty on return?
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

                    if convert_to_quantity:
                        stamps.append(
                            timestamp_to_sinceepoch(stamp))
                    else:
                        stamps.append(stamp)

    return timestamps


def roll_through_session(session_directory, workload_filename, tasks_filename,
        timestamp_keys, convert_to_quantity=False):
    '''Process all matching task and workload files
    from a **workload** execution session.
    Arguments
    ---------
    session_directory
    TODO 
    '''

    filenames = []

    _substr_from_match = lambda s,m: s[ m.a : m.a + m.size ]

    assert isinstance(workload_filename, str)

    if os.path.exists(workload_filename):
        filenames.append(workload_filename)

    else:
        [    # Only 1 file should match!
         filenames.append(os.path.join(session_directory, d))
         if d.find(workload_filename) >= 0 else None
         for d in os.listdir(session_directory)
        ]

    assert len(filenames) == 1

    # pass files for reading to filenames
    # and reduce filenames to longest
    # common 
    if isinstance(tasks_filename, list):
        filenames.extend(tasks_filename)
     #del#   # This gets largest common substring
     #del#   tasks_filename = reduce(
     #del#       lambda r,s: _substr_from_match(
     #del#           r, difflib.SequenceMatcher(
     #del#           None, r, s
     #del#           ).find_longest_match(
     #del#           0, len(r), 0, len(s))
     #del#       ),
     #del#       tasks_filename
     #del#   )

     #del#   assert len(tasks_filename) > 0

    else: 
        [
         filenames.append(os.path.join(session_directory, d))
         if d.find(tasks_filename) >= 0 else None
         for d in os.listdir(session_directory)
        ]

    timestamps = dict()
    timestamps["workload"] = workload_timestamps = list()
    timestamps["task"]     = tasks_timestamps = list()

    for filename in filenames:
        if isinstance(filename, (tuple,list)):
            _tasks_timestamps = [
                get_timestamp_values(
                    os.path.abspath(fnm),
                    timestamp_keys["task"],
                    convert_to_quantity,
                )
                for fnm in filename
            ]
            # FIXME if there were duplicate non-empty keys,
            # this should raise error instead of randomly
            # presenting whichever comes last in comprehension
            tasks_timestamps.append({
                k:v
                for d in _tasks_timestamps
                for k,v in d.items() if v
            })

        else:
            filepath = os.path.abspath(filename)

            if filepath.find(workload_filename) >= 0:
                workload_timestamps.append(
                    get_timestamp_values(
                        filepath,
                        timestamp_keys["workload"],
                        convert_to_quantity))

            else:
                tasks_timestamps.append(
                    get_timestamp_values(filepath,
                        timestamp_keys["task"],
                        convert_to_quantity))

    return timestamps


def timestamp_to_sinceepoch(timestamp, time_format=''):
    '''Convert timestamp to an easily-compared value.
    Here we just use time-since-epoch for quantifying all
    timestamp values
    '''
    # TODO support format given by argument
    possible_formats = [
        '%Y/%m/%d-%H:%M:%S',
        '%Y-%m-%d_%H:%M:%S',
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

