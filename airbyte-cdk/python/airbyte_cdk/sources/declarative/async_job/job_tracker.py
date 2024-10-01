# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import threading
import uuid
from typing import Set

from airbyte_cdk.logger import lazy_log

LOGGER = logging.getLogger("airbyte")


class ConcurrentJobLimitReached(Exception):
    pass


class JobTracker:
    def __init__(self, limit: int):
        self._jobs: Set[str] = set()
        self._limit = limit
        self._lock = threading.Lock()

    def try_to_get_intent(self) -> str:
        lazy_log(LOGGER, logging.DEBUG, lambda: f"JobTracker - Trying to acquire lock by thread {threading.get_native_id()}...")
        with self._lock:
            if self._has_reached_limit():
                raise ConcurrentJobLimitReached("Can't allocate more jobs right now: limit already reached")
            intent = f"intent_{str(uuid.uuid4())}"
            lazy_log(LOGGER, logging.DEBUG, lambda: f"JobTracker - Thread {threading.get_native_id()} has acquired {intent}!")
            self._jobs.add(intent)
            return intent

    def add_job(self, intent_or_job_id: str, job_id: str) -> None:
        if intent_or_job_id not in self._jobs:
            raise ValueError(f"Can't add job: Unknown intent or job id, known values are {self._jobs}")

        if intent_or_job_id == job_id:
            # Nothing to do here as the ID to replace is the same
            return

        lazy_log(
            LOGGER, logging.DEBUG, lambda: f"JobTracker - Thread {threading.get_native_id()} replacing job {intent_or_job_id} by {job_id}!"
        )
        with self._lock:
            self._jobs.add(job_id)
            self._jobs.remove(intent_or_job_id)

    def remove_job(self, job_id: str) -> None:
        """
        If the job is not allocated as a running job, this method does nothing and it won't raise.
        """
        lazy_log(LOGGER, logging.DEBUG, lambda: f"JobTracker - Thread {threading.get_native_id()} removing job {job_id}")
        with self._lock:
            self._jobs.discard(job_id)

    def _has_reached_limit(self) -> bool:
        return len(self._jobs) >= self._limit
