nopaw help
==========

The basic syntax for using `nopaw` is through the `runpaw`
launcher:

    runpaw [configuration] [command] [options]

`nopaw` supports 3 simple commands: `workload`, `verify`
and `analyze`. Each command uses its own options, but
start from the same root configuration to derive their
runtime parameters. Note that the primary configuration
should point to specific configurations for the
different `nopaw` componenets. The full runtime
specification is given by the `runpaw` config files that
store more static information, such as the command
structure for a particular HPC Queue system, combined
with late-bound values from the user and downstream
config files, e.g. for individual tasks. 

Use the following help options to see information about
how to use the `runpaw` launcher and commands.

    # runpaw launcher help
    runpaw -h/--help
    # runpaw command help
    runpaw [command] -h/--help
