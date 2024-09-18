# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import threading
import uuid
from typing import Set


class ConcurrentJobLimitReached(Exception):
    pass


class JobTracker:
    def __init__(self, limit: int):
        self._jobs: Set[str] = set()
        self._limit = limit
        self._lock = threading.Lock()

    def try_to_get_intent(self) -> str:
        with self._lock:
            if self._has_reached_limit():
                raise ConcurrentJobLimitReached("Can't allocate more jobs right now: limit already reached")
            intent = f"intent_{str(uuid.uuid4())}"
            self._jobs.add(intent)
            return intent

    def add_job(self, intent_or_job_id: str, job_id: str) -> None:
        if intent_or_job_id not in self._jobs:
            raise ValueError(f"Can't add job: Unknown intent or job id, known values are {self._jobs}")

        if intent_or_job_id == job_id:
            # Nothing to do here as the ID to replace is the same
            return

        # It is important here that we add the job before removing the other. Given the opposite, `_has_reached_limit` could return `False`
        # for a very brief moment while we don't want to allocate for more jobs.
        self._jobs.add(job_id)
        self._jobs.remove(intent_or_job_id)

    def remove_job(self, job_id: str) -> None:
        """
        If the job is not allocated as a running job, this method does nothing and it won't raise.
        """
        self._jobs.discard(job_id)

    def _has_reached_limit(self) -> bool:
        return len(self._jobs) >= self._limit
