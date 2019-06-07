'''
'''


import argparse


__all__ = [
    "get_parser",
]


def get_parser():
    #-------------------------------------------------#
    # TOP LEVEL parser
    # TODO tricks to get monolithic help
    parser = argparse.ArgumentParser(
        description="Run 'workload', 'verify', or 'analyze' command with PAW",
        add_help=False,
    )
    #-------------------------------------------------#
    # DEFINE subparsers for workload execution,
    #        verification, and analysis paw commands
    subparsers = parser.add_subparsers(
        title="PAW Commands",
        dest="command",
    )
    workload_parser = subparsers.add_parser(
        "workload",
        description="Run a PAW workload",
    )
    verify_parser = subparsers.add_parser(
        "verify",
        description="Verify that a PAW workload ran as expected",
    )
    analyze_parser = subparsers.add_parser(
        "analyze",
        description="Analyze (1 or a series of) nopaw workloads",
    )

    #-------------------------------------------------#
    # DEFINE arguments
    #   - TOP
    parser.add_argument("-v", "--verbose",
        action="store_true",
        help="NotImplemented: Output verbosity level"
    )
    parser.add_argument("-r", "--pawrc",
        default="paw.bashrc",
        help="An RC file must be specifed for PAW runtime configuration"
    )
    parser.add_argument("-c", "--config",
        default="cfg/paw.yml",
        help="An RC file must be specifed for PAW runtime configuration"
    )
    parser.add_argument("-j", "--job_name",
        default="paw",
        help="An RC file must be specifed for PAW runtime configuration"
    )

    #-------------------------------------------------#
    #   - WORKLOAD
    # TODO this is definitely executor level not task
    workload_parser.add_argument("executor",
        help="Specify the desired tasks wrapper",
    )
    workload_parser.add_argument("n_replicates",
        type=int,
        help="Number of task replicates",
    )
    workload_parser.add_argument("n_minutes",
        type=int,
        help="Number of minutes for workload LRMS job",
    )
    workload_parser.add_argument("-n", "--session_name",
        help="Fix a particular session name",
    )
    workload_parser.add_argument("-s", "--session_home",
        default="sessions",
        help="Change the top-level directory for workload sessions",
    )
    workload_parser.add_argument("-i", "--interactive",
        action="store_true",
        help="Run a workload in interactive mode",
    )
    workload_parser.add_argument("-d", "--db_location",
        default="mongo/",
        help="Number of minutes for workload LRMS job",
    )
    workload_parser.add_argument("-t", "--task_args",
        nargs="*",
        help="Collect all task-specific arguments",
    )
  # TODO task-opts catch all as last
  #      --> processed by command runtime
  #  workload_parser.add_argument("datasize",
  #      nargs="?",
  #      help="Specify one of the preset workload operations",
  #  )

    #-------------------------------------------------#
    #   - VERIFY
    verify_parser.add_argument("session_directory",
        help="Single directory for 'verify' command",
    )
    verify_parser.add_argument("n_replicates",
        type=int,
        help="Number of task replicates",
    )
    verify_parser.add_argument("--db_location",
        default="mongo/",
        help="Number of minutes for workload LRMS job",
    )
    verify_parser.add_argument("--db_host",
        default="0.0.0.0",
        help="(Usually don't need to set to verify) host name or IP for database",
    )
    verify_parser.add_argument("--db_port",
        default=27017, type=int,
        help="(Usually don't need to set to verify) database port number on host",
    )
    verify_parser.add_argument("-d", "--db_name",
        default="testdb",
        help="Name of database where workload is stored",
    )
    verify_parser.add_argument("-t", "--task_args",
        nargs="*",
        help="Collect all task-specific arguments",
    )

    #-------------------------------------------------#
    #   - ANALYZE
    analyze_parser.add_argument("session_directory",
        help="Single session dir or parent dir of group for 'analyze' command."
    )
    analyze_parser.add_argument("output_timestamps",
        nargs="?", default="timestamps.txt",
        help="File name for writing timestamps data (within each session)"
    )
    analyze_parser.add_argument("output_analysis",
        nargs="?", default="analysis.txt",
        help="File name for writing analysis data (within each session)"
    )
    analyze_parser.add_argument("output_profile",
        nargs="?", default="profile.txt",
        help="File name for writing profile data (within each session)"
    )
    analyze_parser.add_argument("-p", "--plot",
        default="",
        help="Relative path to plots directory (across given sessions sorted by N replicates)",
    )
    analyze_parser.add_argument("-P", "--profile_plots",
        action="store_true",
        help="Plot workload profile for session found by the given 'session_directories' value",
    )

    #-------------------------------------------------#
    #   - DONE
    return parser
