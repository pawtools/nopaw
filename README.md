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
  - PAW global configuration: `paw.yml`
  - HPC job command, content: `workload.<lrmsname>.yml`
  - HPC task launch command: `launch.<launchername>.yml`
  - HPC user details: `user.yml`
  - HPC layout details: `resource.<resourcename>.yml`

Below these HPC-specific configurations, PAW uses workflow-specific components
that should not change. Right now, the only supported executors are a simple
connector, and a connector with a runtime loop that inspects for signals in
its database representation.
  - PAW task executor: `executor-simple.yml`
  - PAW task executor: `executor-loop.yml`

For any command shown here, you can type `runpaw <command> -h/--help` to get a
usage prompt. 
0. Copy (and edit if necessary) existing
   config files to match your resource
1. `runpaw workload [...]` to configure and launch job
2. wait for LRMS job
3. `runpaw verify [...]` to verify all operations
4. `runpaw analyze [...]` to process timestamp data

## Tests:
--------------------------------
After you check (or as a way of checking) that the configurations are setup
so that PAW runs without error, run these tests as a basic verification of
the functionality. 
```bash
tests/run-all-tests
```

## Usage:
---------
Always source the RC file: 'paw.bashrc'

Run Script Usage:
```bash
runme [runname] [nreplicates] [operation: "read"/"write"]
    optional: [datasize]
```

Verify Script Usage:
```bash
verifyrun [runname] [operation: "read"/"write"] [nreplicates]
    optional: [dbhost] [dbport] [dbname] [datasize]
```

TODO Analyze Script Usage:
```bash
analyzerun [runname] 
```
## Example Run-and-Verify:

--------------------------
From the directory you cloned for install, just
use these simple steps to run nopaw. These
examples are set up identical to the preconfigured
tests.

```bash
source rt.bashrc
# Test the write operation
runme write10 10 write
# read version
runme read10 10 read
```
< ...  wait for run to complete ... >
```bash
verifyrun write10 write 10
```

## Example Run Weak Scaling of Writes:
----------------------------

```bash
source rt.bashrc
scales=( 10 40 120 250 500 1000 2008 4016 8048 16000 )

for scale in "${scales[@]}"
do
  runme weak-w-$scale $scale write
done
```
< ...  wait for jobs to complete ... >
```bash
for scale in "${scales[@]}"
do
  verifyrun weak-w-$scale write $scale
  analyzerun weak-w-$scale write $scale
done
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


