'''
'''

import argparse

__all__ = [
    "paw_parser",
]

def paw_parser():
    # TOP LEVEL parser
    parser = argparse.ArgumentParser(
        description="Run 'workload', 'verify', or 'analyze' command with PAW"
    )
    parser.add_argument("session_directory",
        help=("Single directory for 'workload' or 'verify' commands,",
              " single or glob patter for 'analyze' command.")
    )
    parser.add_argument("-v", "--verbose",
        action="store_true",
        help="NotImplemented: Output verbosity level"
    )

    # DEFINE subparsers for workload execution, verification, and analysis
    subparsers = parser.add_subparsers(
        title="PAW Command"
        dest="command"
    )
    workload_parser = subparsers.add_parser(
        "workload", parents=[parser],
         help="Run a PAW workload",
    )
    verify_parser = subparsers.add_parser(
        "verify", parents=[parser],
        help="Verify that a PAW workload ran as expected",
    )
    analyze_parser = subparsers.add_parser(
        "analyze", parents=[parser],
        help="Analyze (1 or a series of) nopaw workloads",
    )
    # DEFINE subparsers arguments
    #   - WORKLOAD
    #   - VERIFY
    #   - ANALYZE
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
    analyze_parser.add_argument("-c", "--config",
        default="cfg/analyze.yml",
        help="Path to a configuration file"
    )
    analyze_parser.add_argument("-p", "--plot",
        default="",
        help="Relative path to plots directory (across given sessions sorted by N replicates)",
    )
    analyze_parser.add_argument("-P", "--profile_plots",
        action="store_true",
        help="Plot workload profile for session found by the given 'session_directories' value",
    )

    return parser
