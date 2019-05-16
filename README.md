## nopaw- just a pipeline

- TODO new operation types to test file writing via:
       bash wrapper, python script (+subprocess)
- TODO same order of positional arguments
       in `runme` and `verifyrun`
- TODO option to switch between gridfs based
       file data and the in-task-document model
- TODO "pipeline" executors with read/write operations

Simple pipeline for database read and write tests.
A new database is created, and N parallel read/write
operations take place, plus a 60 second sleep.
The sleep is sort of a stand-in for the (still TODO)
pipeline executors.

Simple wrappers are used to place loop-free
communicators onto your HPC in an LRMS job. The
communicators are told to do a read or write
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
```
git clone https://github.com/pawtool/nopaw.git
```

## Tests:
--------------------------------
Run these to check that your platform installed
correctly.
```
git clone https://github.com/pawtool/nopaw.git
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
runme [runname] [nreplicates] [operation: "read"/"write"]
    optional: [datasize]

Verify Script Usage:
verifyrun [runname] [operation: "read"/"write"] [nreplicates]
    optional: [dbhost] [dbport] [dbname] [datasize]

TODO Analyze Script Usage:
analyzerun [runname] 


## Example Run-and-Verify:
--------------------------
From the directory you cloned for install, just
use these simple steps to run nopaw.

```
source rt.bashrc
# Test the write operation
runme write10 10 write
# read version
#runme read10 10 read
```
< ...  wait for run to complete ... >
```
verifyrun write10 write 10
```

## Example Run Weak Scaling of Writes:
----------------------------

```
source rt.bashrc
scales=( 10 40 120 250 500 1000 2008 4016 8048 16000 )

for scale in "${scales[@]}"
do
  runme weak-w-$scale $scale write
done
```
< ...  wait for jobs to complete ... >
```
for scale in "${scales[@]}"
do
  verifyrun weak-w-$scale write $scale
done
```
anylz

