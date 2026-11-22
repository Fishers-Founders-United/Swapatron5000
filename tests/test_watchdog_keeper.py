import builtins
import time
from unittest import mock

import pytest

# Import the Watchdog class from the module we just added
from src.habitats.watchdog_keeper import Watchdog


def _mock_process(stdout_lines, exit_after=None):
    """Create a mock Popen object.

    *stdout_lines* is an iterable of strings that will be yielded by
    ``process.stdout.readline``. If *exit_after* is provided, the mock will
    simulate the process terminating after that many reads.
    """
    mock_proc = mock.Mock()
    # Use an iterator so each call to readline returns the next line
    line_iter = iter(stdout_lines)
    mock_proc.stdout.readline.side_effect = lambda: next(line_iter, "")
    mock_proc.stdout = mock.Mock()
    mock_proc.stdout.readline.side_effect = lambda: next(line_iter, "")
    mock_proc.terminate.side_effect = lambda: None
    mock_proc.kill.side_effect = lambda: None
    mock_proc.wait.side_effect = lambda timeout=None: None
    mock_proc.poll.side_effect = lambda: None
    return mock_proc


@mock.patch("subprocess.Popen")
def test_watchdog_restarts_on_missing_heartbeat(mock_popen):
    # Simulate a process that never emits a heartbeat line
    mock_popen.return_value = _mock_process(["no heartbeat yet\n"] * 3)

    wd = Watchdog(command=["dummy"], check_interval=0.1, timeout=0.2)
    # Run only a few iterations of the loop manually
    wd._start_process()
    # First read – no heartbeat, timer starts
    wd._process_output()
    # Sleep longer than timeout to trigger restart on next iteration
    time.sleep(0.3)
    wd._process_output()
    # Verify that restart was attempted (terminate then start called twice)
    assert mock_popen.call_count == 2


@mock.patch("subprocess.Popen")
def test_watchdog_keeps_running_when_heartbeat_present(mock_popen):
    # Process emits a heartbeat line every iteration
    mock_popen.return_value = _mock_process(["heartbeat ok\n"] * 5)

    wd = Watchdog(command=["dummy"], check_interval=0.1, timeout=0.5)
    wd._start_process()
    # Run several cycles; should never restart because heartbeat is present
    for _ in range(3):
        wd._process_output()
        time.sleep(0.1)
    # Only the initial start should have happened
    assert mock_popen.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
