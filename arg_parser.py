import argparse


def get_args():
    parser = argparse.ArgumentParser(description="Log Parsing Utility")
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="logs.log",
        help="Path to the log file (default: logs.log)",
    )
    parser.add_argument(
        "-t",
        "--time-format",
        type=str,
        default="%H:%M:%S",
        help="Time format used in logs (default: %%H:%%M:%%S)",
    )
    parser.add_argument(
        "-w",
        "--warning-threshold",
        type=int,
        default=5,
        help="Warning threshold in minutes (default: 5)",
    )
    parser.add_argument(
        "-e",
        "--error-threshold",
        type=int,
        default=10,
        help="Error threshold in minutes (default: 10)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        type=str,
        help="Parse all log files in the specified folder",
    )
    return parser.parse_args()
