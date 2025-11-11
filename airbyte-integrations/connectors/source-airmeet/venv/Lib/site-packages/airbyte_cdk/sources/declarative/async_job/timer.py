# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from datetime import datetime, timedelta, timezone
from typing import Optional


class Timer:
    def __init__(self, timeout: timedelta) -> None:
        self._start_datetime: Optional[datetime] = None
        self._end_datetime: Optional[datetime] = None
        self._timeout = timeout

    def start(self) -> None:
        self._start_datetime = self._now()
        self._end_datetime = None

    def stop(self) -> None:
        if self._end_datetime is None:
            self._end_datetime = self._now()

    def is_started(self) -> bool:
        return self._start_datetime is not None

    @property
    def elapsed_time(self) -> Optional[timedelta]:
        if not self._start_datetime:
            return None

        end_time = self._end_datetime or self._now()
        elapsed_period = end_time - self._start_datetime
        return elapsed_period

    def has_timed_out(self) -> bool:
        if not self.is_started():
            return False
        return self.elapsed_time > self._timeout  # type: ignore  # given the job timer is started, we assume there is an elapsed_period

    @staticmethod
    def _now() -> datetime:
        return datetime.now(tz=timezone.utc)
