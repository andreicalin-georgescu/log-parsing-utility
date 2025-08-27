'''
Simple parser for log files.
Contains two main functions: parse_log_file and generate_report.

parse_log_file: receives a log file path and returns a list of log entries.
The log entries are objects containing the following attributes:
- job description
- job pid
- start time
- end time
- duration

generate_report: receives a list of log entries and generates a report.
The report will contain:
- a warning if any job exceeds 5 minutes
- an error if any job exceeds 10 minutes

The warnings and errors will also be accompanied by the job information for troubleshooting
purposes.
'''
