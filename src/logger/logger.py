"""Module for logging"""
from threading import Lock



class Logger:
    """Simple thread-safe logger"""

    class Severity:
        """Logger severities to distinguish different types of logs"""
        INFO = 'INFO'
        ERROR = 'ERROR'

    def __init__(self) -> None:
        self.mutex = Lock()

    def log(self, message: str, severity: Severity = Severity.INFO) -> None:
        """
        Log a message by a single thread,
        to avoid having multiple messages being sent to std out at the same time.

        Args:
            message (message): message to be logged
        """
        with self.mutex:
            print(f'[{severity}]: {message}')
