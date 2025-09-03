# Log Parsing Utility

A simple Python CLI tool to parse log files, analyze job durations, and generate warnings or errors based on configurable thresholds.

## Features

- **Parse log files**: Reads CSV-formatted logs with job description, PID, start/end times, and calculates job durations.
- **Threshold-based reporting**:  
  - **Warning** if a job exceeds a configurable warning threshold (default: 5 minutes).
  - **Error** if a job exceeds a configurable error threshold (default: 10 minutes).
- **Recursive mode**: Optionally parse all `.log` files in a specified directory.
- **Customizable time format**: Specify the time format used in your logs.
- **Robust CLI**: All options are available via command-line arguments.

## Command-Line Arguments

Provided by `arg_parser.py`:

| Argument                | Description                                             | Default         |
|-------------------------|--------------------------------------------------------|-----------------|
| `-f`, `--file`          | Path to the log file                                   | `logs.log`      |
| `-t`, `--time-format`   | Time format used in logs (strftime syntax)             | `%H:%M:%S`      |
| `-w`, `--warning-threshold` | Warning threshold in minutes                      | `5`             |
| `-e`, `--error-threshold`   | Error threshold in minutes                        | `10`            |
| `-r`, `--recursive`     | Parse all `.log` files in the specified folder         | _None_          |

## Example Usage

```sh
python log_parser.py --file mylogs.log --warning-threshold 3 --error-threshold 7
python log_parser.py --recursive ./logs/
```

## Development & Tooling
- Development time: ~90 minutes, including:
- GitHub Actions workflows for linting, security scanning, formatting, and running unit/integration tests.
- **🤖 Copilot Auto-PR Workflow**: Automatically creates draft PRs for issues with sufficient context ([docs](docs/copilot-workflow.md))
- Makefile for fast local setup and common developer tasks.

## Makefile Commands
Command	Description
setup	Install dependencies
format	Format code with Black
lint	Lint code with Ruff
security	Scan for security issues with Bandit
test	Run unit and integration tests with pytest
check	Run all checks (format, lint, security, test)

| Command  | Description            |
| -------- | -----------------------|
| setup    | Install dependencies   |
| format   | Format code with Black |
| lint     | Lint code with Ruff    |
| security | Scan for security issues with Bandit |
| test     | Run unit and integration tests with pytest |
| check    | Run all checks (format, lint, security, test) |

## Quick Start

1. Create a log file with the required format
2. Run the following commands
```sh
make setup && make check
```

## Important mentions and additional improvements:
1. For the purpose of this exercise, AI-assisted development has been used when generating the unit tests, since they border on the scope of the utility tool.
2. As an additional workflow enhancement, next step is to also *integrate GitHub Copilot action in order to dynamically generate sample log files* of the same structure, thus adding variety to the automated testing of the utility tool.
3. In order to save on GitHub Actions runtime, conditionals can be set for the python-validation job in order to run only when *.py files are changed.
