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

import csv
from datetime import datetime, timedelta

LOG_FILE = "logs.log"
TIME_FORMAT = "%H:%M:%S"
WARNING_THRESHOLD = timedelta(minutes=5)
ERROR_THRESHOLD = timedelta(minutes=10)


def parse_log_file(filename):
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
            job_timestamp = datetime.strptime(job_timestamp_string, TIME_FORMAT)

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

def generate_report(jobs):
    for job in jobs:
        duration = job["duration"]
        job_info = f"{job['description']} (PID {job['pid']}) from {job['start_time']} to {job['end_time']} - Duration: {duration}"
        if duration > ERROR_THRESHOLD:
            print(f"ERROR: {job_info}")
        elif duration > WARNING_THRESHOLD:
            print(f"WARNING: {job_info}")
    

if __name__ == "__main__":
    result_jobs = parse_log_file(LOG_FILE)
    generate_report(result_jobs)
