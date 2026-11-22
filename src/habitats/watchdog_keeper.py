import argparse
import subprocess
import sys
import time
from typing import List


class Watchdog:
    """Monitor a subprocess and restart it if a heartbeat is missed.

    The target process is expected to write lines containing the word
    ``heartbeat`` (case‑insensitive) to its standard output at regular intervals.
    """

    def __init__(self, command: List[str], check_interval: float = 5.0, timeout: float = 10.0):
        self.command = command
        self.check_interval = check_interval
        self.timeout = timeout
        self.process: subprocess.Popen | None = None
        self.last_heartbeat = time.time()

    def _start_process(self) -> None:
        """Launch the target command and reset heartbeat timer."""
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.last_heartbeat = time.time()
        print(f"[watchdog] Started process: {' '.join(self.command)}")

    def _terminate_process(self) -> None:
        """Terminate the current process gracefully, force‑kill if needed."""
        if not self.process:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
        print("[watchdog] Process terminated")
        self.process = None

    def _restart_process(self) -> None:
        """Restart the target process and log the event."""
        print("[watchdog] Restarting process due to missed heartbeat")
        self._terminate_process()
        self._start_process()

    def _process_output(self) -> None:
        """Read stdout line‑by‑line and update heartbeat timestamp."""
        assert self.process is not None and self.process.stdout is not None
        for line in self.process.stdout:
            line = line.strip()
            if not line:
                continue
            print(f"[watchdog] stdout: {line}")
            if "heartbeat" in line.lower():
                self.last_heartbeat = time.time()
            # Check timeout after each line to react quickly
            if time.time() - self.last_heartbeat > self.timeout:
                self._restart_process()
                # After restart, break to re‑enter the loop with fresh stdout
                break
        else:
            # Reached EOF – the process likely exited
            print("[watchdog] Process ended unexpectedly, restarting")
            self._restart_process()

    def run(self) -> None:
        """Main loop: start the process and monitor it indefinitely."""
        self._start_process()
        try:
            while True:
                self._process_output()
                # Small sleep to avoid busy‑looping when no output is produced
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("[watchdog] Received KeyboardInterrupt, shutting down")
        finally:
            self._terminate_process()


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watchdog keeper for the Watchdog Kennel habitat")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run and monitor")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between heartbeat checks (default: 5)")
    parser.add_argument("--timeout", type=float, default=10.0, help="Seconds without heartbeat before restart (default: 10)")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    if not args.command:
        print("Error: No command supplied to monitor", file=sys.stderr)
        sys.exit(1)
    watchdog = Watchdog(command=args.command, check_interval=args.interval, timeout=args.timeout)
    watchdog.run()


if __name__ == "__main__":
    main()
