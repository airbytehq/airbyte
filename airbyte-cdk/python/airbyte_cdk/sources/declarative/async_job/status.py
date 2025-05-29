# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from enum import Enum

_TERMINAL = True


class AsyncJobStatus(Enum):
    RUNNING = ("RUNNING", not _TERMINAL)
    COMPLETED = ("COMPLETED", _TERMINAL)
    FAILED = ("FAILED", _TERMINAL)
    TIMED_OUT = ("TIMED_OUT", _TERMINAL)

    def __init__(self, value: str, is_terminal: bool) -> None:
        self._value = value
        self._is_terminal = is_terminal

    def is_terminal(self) -> bool:
        """
        A status is terminal when a job status can't be updated anymore. For example if a job is completed, it will stay completed but a
        running job might because completed, failed or timed out.
        """
        return self._is_terminal
