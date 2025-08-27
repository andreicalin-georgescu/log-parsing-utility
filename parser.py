'''
Simple parser for log files.
Contains two main functions: parse_log_file and generate_report.

parse_log_file: receives a log file path and returns a dictionary of log entries.
The log entries are objects containing the following attributes:
- job description
- job pid
- start time
- end time
- duration

generate_report: receives a dictionary of log entries and generates a report.
The report will contain:
- a warning if any job exceeds 5 minutes
- an error if any job exceeds 10 minutes

The warnings and errors will also be accompanied by the job information for troubleshooting
purposes.
'''
import csv
from datetime import datetime, timedelta

LOG_FILE = "logs.log"
TIME_FORMAT = "%H:%M:%S"
WARNING_THRESHOLD = timedelta(minutes=5)
ERROR_THRESHOLD = timedelta(minutes=10)

def parse_log_file(filename):
    jobs = {}
    outlier_jobs = []

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) != 4:
                # determine action for malformed rows.
                print(f"Skipping malformed row: {row}")
                continue
            job_timestamp_string, job_description, job_status, job_pid = [item.strip() for item in row]
            job_timestamp = datetime.strptime(job_timestamp_string, TIME_FORMAT)

            # create dictionary entry on START log lines
            if job_status == "START":
                jobs[job_pid] = {
                    "job_description": job_description,
                    "job_pid": job_pid,
                    "start_time": job_timestamp,
                    "end_time": None,
                    "duration": None
                }
            # update dictionary entry on END log lines
            elif job_status == "END" and job_pid in jobs:
                jobs[job_pid]["end_time"] = job_timestamp
                jobs[job_pid]["duration"] = job_timestamp - jobs[job_pid]["start_time"]

        # intermediary step to check job dictionary builds correctly
        return jobs

if __name__ == "__main__":
    jobs = parse_log_file(LOG_FILE)
    print(jobs)

