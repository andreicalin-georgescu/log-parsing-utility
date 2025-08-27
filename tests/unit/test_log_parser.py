import io
import csv
import pytest
from datetime import datetime, timedelta
import log_parser
import sys


# Helper to create in-memory CSV log content
def make_log_content(rows):
    output = io.StringIO()
    writer = csv.writer(output)
    for row in rows:
        writer.writerow(row)
    output.seek(0)
    return output


@pytest.fixture
def simple_log():
    # 2 jobs, one normal, one long
    rows = [
        ["12:00:00", "Job A", "START", "111"],
        ["12:03:00", "Job A", "END", "111"],
        ["13:00:00", "Job B", "START", "222"],
        ["13:11:00", "Job B", "END", "222"],
    ]
    return make_log_content(rows)


# Patch sys.argv before importing log_parser to control arg_parser.get_args()
@pytest.fixture(autouse=True)
def patch_sys_argv(monkeypatch):
    # Set default arguments for arg_parser
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "-f", "dummy.csv", "-t", "%H:%M:%S", "-w", "5", "-e", "10"],
    )
    yield


# Helper to create in-memory CSV log content
def make_log_content(rows):
    output = io.StringIO()
    writer = csv.writer(output)
    for row in rows:
        writer.writerow(row)
    output.seek(0)
    return output


@pytest.fixture
def simple_log():
    # 2 jobs, one normal, one long
    rows = [
        ["12:00:00", "Job A", "START", "111"],
        ["12:03:00", "Job A", "END", "111"],
        ["13:00:00", "Job B", "START", "222"],
        ["13:11:00", "Job B", "END", "222"],
    ]
    return make_log_content(rows)


def test_parse_log_file_basic(monkeypatch, simple_log):
    monkeypatch.setattr("builtins.open", lambda *a, **k: simple_log)
    jobs = log_parser.parse_log_file("dummy.csv")
    assert len(jobs) == 2
    assert jobs[0]["description"] == "Job A"
    assert jobs[0]["pid"] == "111"
    assert jobs[0]["duration"] == timedelta(minutes=3)
    assert jobs[1]["description"] == "Job B"
    assert jobs[1]["duration"] == timedelta(minutes=11)


def test_parse_log_file_skips_malformed(monkeypatch):
    rows = [
        ["12:00:00", "Job A", "START", "111"],
        ["12:03:00", "Job A", "END"],  # malformed
        ["13:00:00", "Job B", "START", "222"],
        ["13:11:00", "Job B", "END", "222"],
        ["14:00:00", "Job C", "END", "333"],  # END with no START
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    # Only Job A and Job B should be parsed
    assert len(jobs) == 2
    assert all(j["description"] in ("Job A", "Job B") for j in jobs)


def test_parse_log_file_handles_multiple_starts(monkeypatch):
    rows = [
        ["10:00:00", "Job X", "START", "999"],
        ["10:05:00", "Job X", "START", "999"],  # duplicate START, should overwrite
        ["10:10:00", "Job X", "END", "999"],
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    assert len(jobs) == 1
    # Duration should be 5 minutes (from second START)
    assert jobs[0]["duration"] == timedelta(minutes=5)


def test_parse_log_file_empty(monkeypatch):
    log = make_log_content([])
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    assert jobs == []


def test_parse_log_file_invalid_time(monkeypatch):
    rows = [
        ["notatime", "Job Y", "START", "123"],
        ["12:00:00", "Job Y", "END", "123"],
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    with pytest.raises(ValueError):
        log_parser.parse_log_file("dummy.csv")


def test_parse_log_file_duplicate_end(monkeypatch):
    rows = [
        ["09:00:00", "Job Z", "START", "321"],
        ["09:05:00", "Job Z", "END", "321"],
        ["09:10:00", "Job Z", "END", "321"],  # END with no START
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    assert len(jobs) == 1
    assert jobs[0]["description"] == "Job Z"
    assert jobs[0]["duration"] == timedelta(minutes=5)


def test_parse_log_file_start_without_end(monkeypatch):
    rows = [
        ["08:00:00", "Job Y", "START", "555"],
        ["08:10:00", "Job X", "START", "556"],
        ["08:15:00", "Job X", "END", "556"],
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    # Only Job X should be parsed
    assert len(jobs) == 1
    assert jobs[0]["description"] == "Job X"
    assert jobs[0]["duration"] == timedelta(minutes=5)


def test_parse_log_file_handles_whitespace(monkeypatch):
    rows = [
        [" 15:00:00 ", " Job D ", " START ", " 888 "],
        [" 15:07:00 ", " Job D ", " END ", " 888 "],
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    assert len(jobs) == 1
    assert jobs[0]["description"] == "Job D"
    assert jobs[0]["pid"] == "888"
    assert jobs[0]["duration"] == timedelta(minutes=7)


def test_generate_report_prints_warning_and_error(capsys):
    jobs = [
        {
            "description": "Short Job",
            "pid": "1",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:04:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=4),
        },
        {
            "description": "Warn Job",
            "pid": "2",
            "start_time": datetime.strptime("11:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("11:06:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=6),
        },
        {
            "description": "Error Job",
            "pid": "3",
            "start_time": datetime.strptime("12:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("12:15:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=15),
        },
    ]
    log_parser.generate_report(jobs)
    out = capsys.readouterr().out
    assert "WARNING" in out
    assert "ERROR" in out
    assert "Warn Job" in out
    assert "Error Job" in out
    assert "Short Job" not in out


def test_generate_report_empty(capsys):
    log_parser.generate_report([])
    out = capsys.readouterr().out
    assert out == ""


def test_generate_report_exact_thresholds_and_warning(capsys):
    jobs = [
        {
            "description": "Exactly 5min",
            "pid": "4",
            "start_time": datetime.strptime("13:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("13:05:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=5),
        },
        {
            "description": "Exactly 10min",
            "pid": "5",
            "start_time": datetime.strptime("14:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("14:10:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=10),
        },
    ]
    log_parser.generate_report(jobs)
    out = capsys.readouterr().out
    # Should print WARNING for the 10min job only
    assert "WARNING" in out
    assert "Exactly 10min" in out
    assert "Exactly 5min" not in out
    assert "ERROR" not in out


def test_generate_report_warning_and_error_only_for_thresholds(capsys):
    jobs = [
        {
            "description": "Below warning",
            "pid": "1",
            "start_time": datetime.strptime("09:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("09:04:59", "%H:%M:%S").time(),
            "duration": timedelta(minutes=4, seconds=59),
        },
        {
            "description": "Just above warning",
            "pid": "2",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:05:01", "%H:%M:%S").time(),
            "duration": timedelta(minutes=5, seconds=1),
        },
        {
            "description": "Just above error",
            "pid": "3",
            "start_time": datetime.strptime("11:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("11:10:01", "%H:%M:%S").time(),
            "duration": timedelta(minutes=10, seconds=1),
        },
    ]
    log_parser.generate_report(jobs)
    out = capsys.readouterr().out
    assert "Below warning" not in out
    assert "WARNING" in out
    assert "Just above warning" in out
    assert "ERROR" in out
    assert "Just above error" in out


def test_generate_report_multiple_errors_and_warnings(capsys):
    jobs = [
        {
            "description": "Warn1",
            "pid": "1",
            "start_time": datetime.strptime("08:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("08:06:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=6),
        },
        {
            "description": "Warn2",
            "pid": "2",
            "start_time": datetime.strptime("08:10:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("08:07:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=-3),  # negative duration, edge case
        },
        {
            "description": "Error1",
            "pid": "3",
            "start_time": datetime.strptime("09:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("09:15:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=15),
        },
        {
            "description": "Short",
            "pid": "4",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:01:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=1),
        },
    ]
    log_parser.generate_report(jobs)
    out = capsys.readouterr().out
    assert "Warn1" in out and "WARNING" in out
    assert "Error1" in out and "ERROR" in out
    assert "Short" not in out
    # Negative duration should not trigger warning/error
    assert "Warn2" not in out


def test_generate_report_handles_missing_duration():
    jobs = [
        {
            "description": "No duration",
            "pid": "1",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:01:00", "%H:%M:%S").time(),
            # 'duration' key missing
        }
    ]
    with pytest.raises(KeyError):
        log_parser.generate_report(jobs)


def test_generate_report_handles_non_timedelta_duration(capsys):
    jobs = [
        {
            "description": "String duration",
            "pid": "1",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:01:00", "%H:%M:%S").time(),
            "duration": "not_a_timedelta",
        }
    ]
    # Should not print WARNING or ERROR, but should not crash
    try:
        log_parser.generate_report(jobs)
    except Exception:
        pytest.fail("generate_report should not crash on non-timedelta duration")
    out = capsys.readouterr().out
    assert "WARNING" not in out
    assert "ERROR" not in out


def test_parse_log_file_skips_malformed(monkeypatch):
    rows = [
        ["13:00:00", "Job B", "START", "222"],
        ["13:11:00", "Job B", "END", "222"],
        ["14:00:00", "Job C", "END", "333"],  # END with no START
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    # Only Job B should be parsed
    assert len(jobs) == 1
    assert jobs[0]["description"] == "Job B"


def test_parse_log_file_handles_multiple_starts(monkeypatch):
    rows = [
        ["10:00:00", "Job X", "START", "999"],
        ["10:05:00", "Job X", "START", "999"],  # duplicate START, should overwrite
        ["10:10:00", "Job X", "END", "999"],
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    assert len(jobs) == 1
    # Duration should be 5 minutes (from second START)
    assert jobs[0]["duration"] == timedelta(minutes=5)


def test_parse_log_file_empty(monkeypatch):
    log = make_log_content([])
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    assert jobs == []


def test_parse_log_file_invalid_time(monkeypatch):
    rows = [
        ["notatime", "Job Y", "START", "123"],
        ["12:00:00", "Job Y", "END", "123"],
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    # Should raise ValueError on invalid time format
    with pytest.raises(ValueError):
        log_parser.parse_log_file("dummy.csv")


def test_generate_report_prints_warning_and_error(capsys):
    jobs = [
        {
            "description": "Short Job",
            "pid": "1",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:04:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=4),
        },
        {
            "description": "Warn Job",
            "pid": "2",
            "start_time": datetime.strptime("11:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("11:06:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=6),
        },
        {
            "description": "Error Job",
            "pid": "3",
            "start_time": datetime.strptime("12:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("12:15:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=15),
        },
    ]
    log_parser.generate_report(jobs)
    out = capsys.readouterr().out
    assert "WARNING" in out
    assert "ERROR" in out
    assert "Warn Job" in out
    assert "Error Job" in out
    assert "Short Job" not in out


def test_generate_report_empty(capsys):
    log_parser.generate_report([])
    out = capsys.readouterr().out
    assert out == ""


def test_generate_report_exact_thresholds_and_warning(capsys):
    jobs = [
        {
            "description": "Exactly 5min",
            "pid": "4",
            "start_time": datetime.strptime("13:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("13:05:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=5),
        },
        {
            "description": "Exactly 10min",
            "pid": "5",
            "start_time": datetime.strptime("14:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("14:10:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=10),
        },
    ]
    log_parser.generate_report(jobs)
    out = capsys.readouterr().out
    # Should print WARNING for the 10min job only
    assert "WARNING" in out
    assert "Exactly 10min" in out
    assert "Exactly 5min" not in out
    assert "ERROR" not in out


def test_generate_report_warning_and_error_only_for_thresholds(capsys):
    jobs = [
        {
            "description": "Below warning",
            "pid": "1",
            "start_time": datetime.strptime("09:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("09:04:59", "%H:%M:%S").time(),
            "duration": timedelta(minutes=4, seconds=59),
        },
        {
            "description": "Just above warning",
            "pid": "2",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:05:01", "%H:%M:%S").time(),
            "duration": timedelta(minutes=5, seconds=1),
        },
        {
            "description": "Just above error",
            "pid": "3",
            "start_time": datetime.strptime("11:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("11:10:01", "%H:%M:%S").time(),
            "duration": timedelta(minutes=10, seconds=1),
        },
    ]
    log_parser.generate_report(jobs)
    out = capsys.readouterr().out
    assert "Below warning" not in out
    assert "WARNING" in out
    assert "Just above warning" in out
    assert "ERROR" in out
    assert "Just above error" in out


def test_generate_report_multiple_errors_and_warnings(capsys):
    jobs = [
        {
            "description": "Warn1",
            "pid": "1",
            "start_time": datetime.strptime("08:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("08:06:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=6),
        },
        {
            "description": "Warn2",
            "pid": "2",
            "start_time": datetime.strptime("08:10:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("08:07:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=-3),  # negative duration, edge case
        },
        {
            "description": "Error1",
            "pid": "3",
            "start_time": datetime.strptime("09:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("09:15:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=15),
        },
        {
            "description": "Short",
            "pid": "4",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:01:00", "%H:%M:%S").time(),
            "duration": timedelta(minutes=1),
        },
    ]
    log_parser.generate_report(jobs)
    out = capsys.readouterr().out
    assert "Warn1" in out and "WARNING" in out
    assert "Error1" in out and "ERROR" in out
    assert "Short" not in out
    # Negative duration should not trigger warning/error
    assert "Warn2" not in out


def test_generate_report_handles_missing_duration(monkeypatch, capsys):
    jobs = [
        {
            "description": "No duration",
            "pid": "1",
            "start_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
            "end_time": datetime.strptime("10:01:00", "%H:%M:%S").time(),
            # 'duration' key missing
        }
    ]
    # Should raise KeyError
    with pytest.raises(KeyError):
        log_parser.generate_report(jobs)


def test_parse_log_file_handles_whitespace(monkeypatch):
    rows = [
        [" 15:00:00 ", " Job D ", " START ", " 888 "],
        [" 15:07:00 ", " Job D ", " END ", " 888 "],
    ]
    log = make_log_content(rows)
    monkeypatch.setattr("builtins.open", lambda *a, **k: log)
    jobs = log_parser.parse_log_file("dummy.csv")
    assert len(jobs) == 1
    assert jobs[0]["description"] == "Job D"
    assert jobs[0]["pid"] == "888"
    assert jobs[0]["duration"] == timedelta(minutes=7)
