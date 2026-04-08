# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Iterator, List, Optional

from .async_job import AsyncJob, update_in_batch  # ParentAsyncJob not needed here


if TYPE_CHECKING:  # pragma: no cover
    from source_facebook_marketing.api import API

logger = logging.getLogger("airbyte")


class APILimit:
    """
    Centralizes throttle/concurrency. Jobs call try_consume() before starting,
    and must call release() exactly once when they finish (success/skip/fail/timeout).
    """

    # Conservative default to avoid exhausting Facebook's ad-account-level API quota.
    # Previous default of 100 caused rate-limit failures on accounts with many ads.
    DEFAULT_MAX_JOBS = 10

    # When throttle is high, wait this long before re-checking.
    THROTTLE_WAIT_INTERVAL = timedelta(minutes=2)
    MAX_THROTTLE_WAIT = timedelta(minutes=15)

    def __init__(
        self,
        api,
        account_id: str,
        *,
        throttle_limit: float = 90.0,
        max_jobs: int = DEFAULT_MAX_JOBS,
    ):
        self._api = api
        self._account_id = account_id
        self.throttle_limit = throttle_limit
        self.max_jobs = max_jobs

        self._current_throttle: float = 0.0
        self._inflight: int = 0

    # --- Throttle ---

    def refresh_throttle(self) -> None:
        """
        Ping the account to refresh the `x-fb-ads-insights-throttle` header and cache the value.
        If the throttle is above the limit, wait with exponential backoff before returning,
        giving the API quota time to recover.
        """
        total_waited = timedelta()
        wait_interval = self.THROTTLE_WAIT_INTERVAL

        while True:
            self._api.get_account(account_id=self._account_id).get_insights()
            t = self._api.api.ads_insights_throttle
            self._current_throttle = max(getattr(t, "per_account", 0.0), getattr(t, "per_application", 0.0))

            if self._current_throttle < self.throttle_limit:
                break

            if total_waited >= self.MAX_THROTTLE_WAIT:
                logger.warning(
                    "Throttle still at %.1f%% after waiting %s; proceeding without further delay.",
                    self._current_throttle,
                    total_waited,
                )
                break

            logger.info(
                "Throttle at %.1f%% (limit %.1f%%); waiting %s for quota recovery.",
                self._current_throttle,
                self.throttle_limit,
                wait_interval,
            )
            time.sleep(wait_interval.total_seconds())
            total_waited += wait_interval
            wait_interval = min(
                wait_interval * 2,
                self.MAX_THROTTLE_WAIT - total_waited + timedelta(seconds=1),
            )

    @property
    def limit_reached(self) -> bool:
        return self._inflight >= self.max_jobs or self._current_throttle >= self.throttle_limit

    @property
    def capacity_reached(self) -> bool:
        return self._inflight >= self.max_jobs

    # --- Capacity accounting ---

    def release(self) -> None:
        """Called by jobs when the remote run reaches a terminal state (completed/failed/skipped/timeout)."""
        if self._inflight > 0:
            self._inflight -= 1

    def try_consume(self) -> bool:
        """
        Reserve capacity for one new job if both throttle and concurrency allow it.
        Jobs should call this right before actually starting the AdReportRun.
        """
        # No point in checking throttle if we are already at max concurrency.
        if self.capacity_reached:
            return False
        self.refresh_throttle()
        if self.limit_reached:
            return False
        self._inflight += 1
        return True

    # --- Introspection (optional logging) ---

    @property
    def inflight(self) -> int:
        return self._inflight

    @property
    def current_throttle(self) -> float:
        return self._current_throttle


class InsightAsyncJobManager:
    """
    Minimal, state-agnostic manager:
      - asks jobs to start when capacity allows (jobs decide if they can start)
      - polls jobs in batch for status updates
      - yields completed jobs
      - accepts 'new_jobs' emitted by jobs (e.g., after split) and puts them into the running set
    """

    JOB_STATUS_UPDATE_SLEEP_SECONDS = 30

    def __init__(
        self,
        api: "API",
        jobs: Iterator[AsyncJob],
        account_id: str,
        *,
        throttle_limit: float = 90.0,
        max_jobs_in_queue: int = APILimit.DEFAULT_MAX_JOBS,
    ):
        self._api = api
        self._account_id = account_id
        self._jobs = iter(jobs)
        self._running_jobs: List[AsyncJob] = []
        self._prefetched_job: Optional[AsyncJob] = None  # look-ahead buffer
        self._api_limit = APILimit(
            self._api,
            self._account_id,
            throttle_limit=throttle_limit,
            max_jobs=max_jobs_in_queue,
        )

    # --- Public consumption API ---

    def completed_jobs(self) -> Iterator[AsyncJob]:
        while self._running_jobs or self._has_more_jobs():
            self._start_jobs()

            completed = self._check_jobs_status()
            if completed:
                yield from completed
            else:
                logger.info(f"No jobs ready to be consumed, wait for {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
                time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)

    # --- Internals ---

    def _check_jobs_status(self) -> List[AsyncJob]:
        """
        Batch-poll all running jobs. Collect completed ones. If a job produced
        additional work (via job.new_jobs), put those into the running set.
        """
        completed_jobs: List[AsyncJob] = []

        # Ask each job to update itself. For plain jobs, this batches directly;
        # for parent jobs, their update_job implementation will update children.
        update_in_batch(api=self._api.api, jobs=self._running_jobs)

        new_running: List[AsyncJob] = []
        for job in self._running_jobs:
            if job.completed:
                completed_jobs.append(job)
            else:
                # If the job emitted new work (e.g., via split), take its `new_jobs` instead of keeping the parent.
                # This effectively "clears" the old job from the running set: we replace it with its children.
                new_jobs = job.new_jobs
                if new_jobs:
                    new_running.extend(new_jobs)
                else:
                    # Keep the job in running set if it hasn't finished.
                    new_running.append(job)

        self._running_jobs = new_running

        logger.info(
            "Manager status: completed=%d, running=%d, inflight=%d, throttle=%.2f",
            len(completed_jobs),
            len(self._running_jobs),
            self._api_limit.inflight,
            self._api_limit.current_throttle,
        )
        return completed_jobs

    def _start_jobs(self) -> None:
        """
        Phase 1: give already-running jobs a chance to start more internal work
                 (useful for ParentAsyncJob that staggers children).
        Phase 2: pull fresh jobs from the upstream iterator while capacity allows.
        NOTE: jobs themselves decide whether they can start by consulting APILimit.
        """
        # Phase 1 — let existing running jobs opportunistically start internal work.
        for job in self._running_jobs:
            if not job.started:
                # Simple job: (re)starts itself if capacity allows — including retries after failure.
                # Parent job: typically starts some children and remains 'not fully started' until all children started.
                job.start(self._api_limit)
                if self._api_limit.limit_reached:
                    return

        if self._api_limit.capacity_reached:
            # No point in trying to start new jobs if we are at max concurrency.
            return

        # Phase 2 — schedule new jobs while there is capacity.
        while True:
            next_job = self._pull_next_job()
            if not next_job:
                break

            next_job.start(self._api_limit)
            # Regardless of whether it could start immediately, keep it in the running set.
            # It will attempt to start again in Phase 1 on subsequent cycles.
            self._running_jobs.append(next_job)

            if self._api_limit.limit_reached:
                break

    def _pull_next_job(self) -> Optional[AsyncJob]:
        if self._prefetched_job is not None:
            pulled_job, self._prefetched_job = self._prefetched_job, None
            return pulled_job
        return next(self._jobs, None)

    def _has_more_jobs(self) -> bool:
        if self._prefetched_job is not None:
            return True
        self._prefetched_job = next(self._jobs, None)
        return self._prefetched_job is not None
