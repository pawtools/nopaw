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
    workload_parser.add_argument("session_directory",
        help="Single directory for 'workload' command",
    )
    workload_parser.add_argument("task_name",
        help="Specify the desired task (must have matching config task.<task_name>.yml)",
    )
    workload_parser.add_argument("n_replicates",
        type=int,
        help="Number of task replicates",
    )
    workload_parser.add_argument("n_minutes",
        type=int,
        help="Number of minutes for workload LRMS job",
    )
    workload_parser.add_argument("-d", "--db_location",
        default="mongo/",
        help="Number of minutes for workload LRMS job",
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

    #-------------------------------------------------#
    #   - ANALYZE
    analyze_parser.add_argument("session_directory",
        help="Single or glob pattern for 'analyze' command."
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
