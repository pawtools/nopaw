## nopaw- just a pipeline

Simple workload pipeline for testing software on HPCs and computer clusters.
nopaw abstracts computational work with this model:

  -  `job`      --> instructions to `launch` components (usually for particular `workload`)
  -  `workload` --> set of independent `task`s (executed in LRMS `submit`'d `job` on HPC)
  -  `executor` --> `launch`'d, database synched wrapper who `run`s `task`s


nopaw's executors recieve runtime signals that can propagate
steering commands or otherwise modify the state of tasks and 
executors. This is implemented by an asynchronous execution model
where `executor`s poll the database for `task`s and `run` them, while
also continually checking for `signal`s in database.

Simple wrappers are used to place executors onto your HPC in an LRMS job.
The executors are told to do a task when you launched the job, and perform
the operation after they are distributed on the HPC, then shutdown.

![nopaw execution sequence](https://raw.githubusercontent.com/pawtools/nopaw/branch/nopaw-sequence.png)

Simple `read` and `write` operations are provided to demonstrate the infrastructure and
verify basic operations. A number of timestamps are reported,
which can be analyzed to understand the maximum
possible performance of a Workflow Management System
built on the particular database in the tested
HPC environment. Instructions for these test cases are in this README.
For examples of creating basic workload configurations yourself, see the tutorials section.
All tutorial examples can be run as introduced with nopaw out-of-the-box. 

With the simple `read` and `write` tasks, there are a small number of control parameters that
can be varied to understand how the performance
changes in response to expectable stressors:

 - Operation Type: read or write
 - Scale: n replicates
 - Data Size: size and unit (blank=k, m)
 - Executor Layout: executors per node (max 1 per cpu)


Currently nopaw MongoDB as database and PyMongo to interface.
Could easily provide wrappers for simple operations
with other databases, or exchange the PyMongo
connector/Python Executor with other interfaces
such as C++, Java, etc.

## Install:
-----------
There will be a message about mongodb since there is a limited ability to easily
install this compared with the rest of the software. If you can use a freely
downloaded version, replace/use the given value from the variable "MONGODB_VERSION"
in the installer.
```bash
git clone https://github.com/pawtool/nopaw.git
cd nopaw
./install.sh
```

## Steps before Runtime:
------------------------
Run the 4 steps below to check that your platform installed completely and that you have
configured it to run correctly on your HPC system. Note that you must specify
a number of runtime system details in the configuration files under `cfg` subdirectory.
Troubleshooting issues
with your config should feel almost exactly the same as running a command manually, and
fixing the reported errors that may come up. i.e. if you try to `bsub`/`qsub` and the
LRMS gives an error that you need some option, add it to the configs by copying an
existing line in the `workload` `option` section and modify it according to the error
and/or documentation your admin provide. Every HPC and user thereof requires these files
are filled out correctly for PAW to launch its components correctly. 
  - PAW global configuration: `paw.yml` --> points to each component config so you can choose from many
  - HPC job command, job script content: `workload.<lrmsname>.yml`
  - HPC task launch command: `launch.<launchername>.yml`
  - HPC user details: `user.yml`
  - HPC layout details: `resource.<resourcename>.yml`

Below these HPC-specific configurations, PAW uses workflow-specific components
that should not change. Right now, the only supported executors are a simple
connector, and a connector with a runtime loop that inspects for signals in
its database representation.
  - PAW task executor: `executor-simple.yml`
  - PAW task executor: `executor-loop.yml`

For any command shown here, you can type `runpaw <command> -h/--help` to get
usage help. 
 - 0. Copy (and edit if necessary) existing config files to match your resource
 - 1. `runpaw workload [...]` to configure and launch job
 - 2. wait for LRMS job
 - 3. `runpaw verify [...]` to verify all operations
 - 4. `runpaw analyze [...]` to process timestamp data

## Usage:
---------
Always source the RC file: 'paw.bashrc'

Run Script Usage:
```bash
runpaw [global options] <command> [command options] -t [task options]
```

There are 3 commands: `workload`, `verify`, and `analyze` that are self
explanatory. The built-in `read` and `write` tasks are run through a
workload like this (`-v` for verbose to see what PAW is doing):
```bash
#         command   task-executor   replicates  minutes   operation
runpaw -v workload executor-simple     10         10   -t   write
runpaw -v workload executor-simple     10         10   -t   read
```

These tasks have pre-programmed verifications to make sure everything
happened that should have (each task did the `read`/`write` successfully).
Verifying reads sort-of happens at runtime as each guy checks the data
it read against an in-memory copy of the data that is typed in a script,
however with writes the database that was written to is instantiated
and each task's entry checked against the in-script data.
```bash
#         command session-dir  replicates  operation
runpaw -v verify sessions/0001    10        -t write   # same order
runpaw -v verify sessions/0002    10        -t read    # as above
```
How do we know what directories? We didn't give a name for these workload sessions,
so they were just generated by a counter. In the examples or with the help option,
you can see how to give specific name to easily track work and resulting logs.
With `analyze` and `verify` you always have to explicitly give existing session folder(s).

Some pre-programmed analysis is possible with optional plots.
```bash
#         command  session-dir  replicates  operation
runpaw -v analyze sessions/0001    10        -t write   # same order
runpaw -v analyze sessions/0002    10        -t read    # as above
```

## Tests:
--------------------------------
After you check (or as a way of checking) that the configurations are setup
so that PAW runs without error, run these tests as a basic verification of
the functionality. 
```bash
tests/run-rw-tests
```

## Example Run Weak Scaling of Writes:
----------------------------
Example: weak scaling experiment for writes.
Here we add an option `-n` to specify specific names for each workload execution
session, which you should always do when you need to track them directly.
```bash
source paw.bashrc
#scales=( 10 42 168 672 2688 10752 )
scales=( 10 20 30 )
minutes=10

for scale in "${scales[@]}"; do
  runpaw -v workload executor-simple $scale $minutes -n ws-$scale -t write
done
```

< ...  wait for jobs to complete ... >
```bash
for scale in "${scales[@]}"; do
  runpaw -v verify sessions/ws-$scale $scale -t write
done

# this measures execution times for all guys under parent folder
# and creates plot with all data together with name "filename-weak-scaling.png"
runpaw -v analyze sessions -p sessions/filename
```

Note that another useful `workload` option `-s` is used to change the session home for different
groups of data such as putting all sessions for this weak scaling experiment into
a single directory like this (can be combined with `-n` or alone)
```bash
# use current sessions above this group
sessions=sessions/ws
## or put this group at top nopaw directory
#sessions=ws
runpaw -v workload executor-simple $scale $minutes -s $sessions -n ws-$scale -t write
```



- TODO write basic test routines:
       read/write - 1. (live) execution unit test with
                    runme followed by 2. verifyrun
       verifyrun  - 1. use pre-existing read-10/write-10
                    to 2. ensure verify methods continue
                    to give expected result
       analyzerun - 1. use pre-existing read-10/write-10
                    to 2. ensure analysis methods continue
                    to give expected result

       each of these 3 test modes should be run with
       each of the task/operation types

- TODO new operation types to test file writing via:
       bash wrapper, python script (+subprocess)

- TODO option to switch between gridfs based
       file data and the in-task-document model


