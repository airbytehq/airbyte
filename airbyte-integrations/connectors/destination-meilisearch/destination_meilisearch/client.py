#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
import time
from typing import Any, Callable, Iterable, List, Optional, TypeVar

from meilisearch import Client
from meilisearch.errors import MeilisearchApiError, MeilisearchCommunicationError, MeilisearchTimeoutError
from meilisearch.models.task import TaskInfo


logger = logging.getLogger("airbyte")

T = TypeVar("T")

# Statuses that indicate a temporary condition on the server or a proxy in
# front of it. Any other API error is a problem with the request itself.
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 6
MAX_BACKOFF_SECONDS = 30.0

# Task statuses are polled in groups of this many task UIDs, which keeps the
# request URL reasonably short.
TASK_POLL_BATCH_SIZE = 100
MIN_TASK_POLL_DELAY_SECONDS = 0.05
MAX_TASK_POLL_DELAY_SECONDS = 2.0
TASK_WAIT_LOG_EVERY_SECONDS = 60.0

# Timeout for a single HTTP request. Document payloads can be large, so this is
# generous.
REQUEST_TIMEOUT_SECONDS = 300


class TaskFailedError(Exception):
    """A Meilisearch task which did not succeed.

    Write requests are processed asynchronously, so problems with a request's
    content (an invalid document, for example) are only reported through its
    task.
    """

    def __init__(self, task: Any):
        self.task = task
        self.code = (task.error or {}).get("code")
        if task.status == "canceled":
            message = f"{task.type} task {task.uid} for index '{task.index_uid}' was canceled"
        else:
            error = task.error or {}
            message = f"{task.type} task {task.uid} for index '{task.index_uid}' failed: {error.get('message')} ({error.get('code')})"
        super().__init__(message)


def is_retryable(err: Exception) -> bool:
    if isinstance(err, (MeilisearchCommunicationError, MeilisearchTimeoutError)):
        return True
    return isinstance(err, MeilisearchApiError) and err.status_code in RETRYABLE_STATUS_CODES


def with_retry(
    description: str,
    fn: Callable[[], T],
    sleep: Callable[[float], None] = time.sleep,
    max_attempts: int = MAX_ATTEMPTS,
) -> T:
    """Calls fn until it succeeds, fails with an error that isn't retryable, or
    has been attempted max_attempts times.

    The Meilisearch client does not retry requests itself. Retrying an enqueued
    write is safe because documents are keyed by their ID, except for documents
    of append streams, where a retried request may add a document twice. This
    is no different from the at-least-once delivery of append syncs.
    """
    attempt = 1
    while True:
        try:
            return fn()
        except Exception as err:
            if not is_retryable(err) or attempt >= max_attempts:
                raise
            delay = min(2 ** (attempt - 1), MAX_BACKOFF_SECONDS)
            logger.warning(f"Retrying '{description}' in {delay}s after attempt {attempt} failed: {err}")
            sleep(delay)
            attempt += 1


def api_error_code(err: Exception) -> Optional[str]:
    return getattr(err, "code", None) if isinstance(err, MeilisearchApiError) else None


class MeiliClient:
    """Wraps the Meilisearch client with retries and task tracking.

    The underlying client shares mutable request headers between requests, so
    it must not be used from more than one thread.
    """

    def __init__(
        self,
        host: str,
        api_key: Optional[str],
        sleep: Callable[[float], None] = time.sleep,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
        max_attempts: int = MAX_ATTEMPTS,
    ):
        self.client = Client(host.rstrip("/"), api_key or None, timeout=timeout, client_agents=("Airbyte",))
        self._sleep = sleep
        self._max_attempts = max_attempts

    def _retry(self, description: str, fn: Callable[[], T]) -> T:
        return with_retry(description, fn, self._sleep, self._max_attempts)

    def enqueue(self, description: str, fn: Callable[[], TaskInfo]) -> int:
        """Sends a request that enqueues a task, and returns the task's UID."""
        return self._retry(description, fn).task_uid

    def run(self, description: str, fn: Callable[[], TaskInfo]) -> None:
        """Sends a request that enqueues a task, and waits for the task to succeed."""
        self.wait_for_tasks([self.enqueue(description, fn)])

    def wait_for_tasks(self, uids: Iterable[int]) -> None:
        """Waits for every task to finish, and raises TaskFailedError if any of
        them failed or was canceled.

        Rather than waiting for each task in turn, all pending tasks are polled
        together, starting with a short delay that grows while tasks remain.
        """
        pending: List[int] = list(uids)
        delay = MIN_TASK_POLL_DELAY_SECONDS
        start = last_log = time.monotonic()

        while pending:
            still_pending: List[int] = []
            oldest_pending = None
            for i in range(0, len(pending), TASK_POLL_BATCH_SIZE):
                chunk = pending[i : i + TASK_POLL_BATCH_SIZE]
                result = self._retry(
                    "get tasks",
                    lambda: self.client.get_tasks({"uids": [str(uid) for uid in chunk], "limit": len(chunk)}),
                )
                found = set()
                for task in result.results:
                    found.add(task.uid)
                    if task.status == "succeeded":
                        continue
                    if task.status in ("failed", "canceled"):
                        raise TaskFailedError(task)
                    still_pending.append(task.uid)
                    if oldest_pending is None or task.uid < oldest_pending.uid:
                        oldest_pending = task

                missing = [uid for uid in chunk if uid not in found]
                if missing:
                    # Meilisearch deletes the oldest finished tasks once its task
                    # queue is full, so a missing task can't be assumed to have
                    # succeeded.
                    raise RuntimeError(f"Task {missing[0]} was not found: it may have been deleted before its status could be read")

            pending = still_pending
            if not pending:
                break

            now = time.monotonic()
            if now - last_log >= TASK_WAIT_LOG_EVERY_SECONDS:
                logger.info(
                    f"Waiting for Meilisearch to process {len(pending)} tasks ({int(now - start)}s elapsed). "
                    f"The oldest is {oldest_pending.type} task {oldest_pending.uid} for index '{oldest_pending.index_uid}', which is {oldest_pending.status}"
                )
                last_log = now

            self._sleep(delay)
            delay = min(delay * 2, MAX_TASK_POLL_DELAY_SECONDS)

    def get_index_primary_key(self, uid: str) -> Optional[str]:
        """Returns the primary key of an index, an empty string if it has none,
        or None if the index doesn't exist."""
        try:
            info = self._retry("get index", lambda: self.client.http.get(f"indexes/{uid}"))
        except MeilisearchApiError as err:
            if err.code == "index_not_found":
                return None
            raise
        return info.get("primaryKey") or ""

    def ensure_index(self, uid: str, primary_key: str) -> None:
        """Creates an index with the given primary key, or checks that an
        existing index has a compatible primary key."""
        existing = self.get_index_primary_key(uid)
        if existing is None:
            try:
                self.run(f"create index '{uid}'", lambda: self.client.create_index(uid, {"primaryKey": primary_key}))
                return
            except TaskFailedError as err:
                # The index may have been created concurrently.
                if err.code != "index_already_exists":
                    raise
            existing = self.get_index_primary_key(uid) or ""

        if existing == primary_key:
            return
        if existing == "":
            # An index without a primary key can't have any documents yet.
            self.run(
                f"set primary key of index '{uid}'",
                lambda: self.client.index(uid).update(primary_key=primary_key),
            )
            return
        raise ValueError(
            f"Index '{uid}' already exists with primary key '{existing}', but this destination requires the primary key '{primary_key}'. "
            "Delete the index, or sync the stream to a different index."
        )

    def ensure_filterable(self, uid: str, attribute: str) -> None:
        """Adds an attribute to the filterable attributes of an index, keeping
        the attributes that are already filterable."""
        index = self.client.index(uid)
        # Attributes are names, or objects with attribute patterns which are
        # kept as-is.
        current = self._retry("get filterable attributes", index.get_filterable_attributes) or []
        if attribute in current:
            return
        self.run(
            f"make '{attribute}' filterable in index '{uid}'",
            lambda: index.update_filterable_attributes(list(current) + [attribute]),
        )
