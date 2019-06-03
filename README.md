## nopaw- just a pipeline

Simple workload pipeline for testing software on HPCs and computer clusters.
nopaw abstracts computational work with this model:

   `job`      --> instructions to `launch` components (usually for particular `workload`)
   `workload` --> set of independent `task`s (executed in LRMS `submit`'d `job` on HPC)
   `executor` --> `launch`'d, database synched wrapper who `run`s `task`s


nopaw's executors have runtime slots to allow signal propagation
for steering or otherwise modifying any current tasks through their 
executors. This is implemented by an asynchronous execution model
where `executor`s poll the database for `task`s and `run` them, while
continually checking for `signal`s in database `slot`s.

Simple wrappers are used to place loop-free
communicators onto your HPC in an LRMS job. The
communicators are told to do a `read` or `write`
operation when you launched the job, and perform
the operation after they are distributed on the
HPC, then shutdown following their sleep.

![nopaw execution sequence](https://raw.githubusercontent.com/pawtools/nopaw/branch/nopaw-sequence.png)

The reads or writes can then be verified for data
integrity. A number of timestamps are reported,
which can be analyzed to understand the maximum
possible performance of a Workflow Management System
built on the particular database in the tested
HPC environment.

There are a small number of control parameters that
can be varied to understand how the performance
changes in response to expectable stressors:

 - Scale: n replicates
 - Operation Type: read or write
 - Data Size: size and unit (blank=k, m)
 - Layout Factor: communicators per node

Currently nopaw MongoDB as database and PyMongo to
interface.
Could easily provide wrappers for simple operations
with other databases, or exchange the PyMongo
connector/Python Executor with other interfaces
such as C++, Java, etc.

## Install:
-----------
```bash
git clone https://github.com/pawtool/nopaw.git
cd nopaw
./install.sh
```

## Tests:
--------------------------------
Run these to check that your platform installed
correctly. Note that you must correctly specify
a small number of runtime system details in the
configuration file `workload.yml`.
```bash
tests/run-all-tests
```

## Steps:
---------
0. Copy (and edit if necessary) existing
   LRMS config file to match your resource
1. `runme` to configure and launch job
2. wait for LRMS job
3. `verifyrun` to verify all operations
4. `analyzerun` to process timestamp data

## Usage:
---------
Always source the RC file: 'rt.bashrc'

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


