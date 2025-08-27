"""
Simple parser for log files.
Contains two main functions: parse_log_file and generate_report.

parse_log_file: receives a log file path and returns a list of jobs.
The log entries are objects containing the following attributes:
- job description
- job pid
- start time
- end time
- duration

generate_report: receives a list of jobs and generates a report.
The report will contain:
- a warning if any job exceeds 5 minutes
- an error if any job exceeds 10 minutes

The warnings and errors will also be accompanied by the job information for troubleshooting
purposes.
"""
import os
import csv
from datetime import datetime, timedelta
from arg_parser import get_args

def parse_log_file(filename, time_format ="%H:%M:%S"):
    jobs = {}
    result_jobs = []

    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) != 4:

                # determine action for malformed rows.
                print(f"Skipping malformed row: {row}")
                continue
            job_timestamp_string, job_description, job_status, job_pid = [
                item.strip() for item in row
            ]
            job_timestamp = datetime.strptime(job_timestamp_string, time_format)

            # add dictionary entry on START log lines with the timestamp value
            if job_status == "START":
                jobs[job_pid] = job_timestamp

            # on END log lines, pop the timestamp value from the job_pid key
            elif job_status == "END":
                start_time = jobs.pop(job_pid, None)
                if start_time:
                    # Check if duration can be successfully calculated
                    try:
                        job_duration = job_timestamp - start_time
                    except Exception as e:
                        print(f"Error calculating duration for {job_description}: {e}")
                    result_jobs.append(
                        {
                            "description": job_description,
                            "pid": job_pid,
                            "start_time": start_time.time(),
                            "end_time": job_timestamp.time(),
                            "duration": job_duration,
                        }
                    )
    return result_jobs

def generate_report(
        jobs,
        warning_threshold=timedelta(minutes=5),
        error_threshold=timedelta(minutes=10)
):
    for job in jobs:
        duration = job["duration"]
        # Check if duration is timedelta
        if not isinstance(duration, timedelta):
            print(f"Invalid duration for job {job['description']}: {duration}")
            continue
        
        job_info = f"{job['description']} (PID {job['pid']}) from {job['start_time']} to {job['end_time']} - Duration: {duration}"
        if duration > error_threshold:
            print(f"ERROR: {job_info}")
        elif duration > warning_threshold:
            print(f"WARNING: {job_info}")
    

if __name__ == "__main__":
    args = get_args()
    LOG_FILE = args.file
    TIME_FORMAT = args.time_format
    WARNING_THRESHOLD = timedelta(minutes=args.warning_threshold)
    ERROR_THRESHOLD = timedelta(minutes=args.error_threshold)

    if args.recursive:
        for filename in os.listdir(args.recursive):
            if filename.endswith(".log"):
                print(f"Parsing log file: {filename}")
                result_jobs = parse_log_file(
                    os.path.join(args.recursive, filename),
                    time_format=TIME_FORMAT
                )
                generate_report(
                    result_jobs,
                    warning_threshold=WARNING_THRESHOLD,
                    error_threshold=ERROR_THRESHOLD
                )
    else:
        result_jobs = parse_log_file(LOG_FILE, time_format=TIME_FORMAT)
        generate_report(
            result_jobs,
            warning_threshold=WARNING_THRESHOLD,
            error_threshold=ERROR_THRESHOLD
        )
