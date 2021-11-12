#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from enum import Enum
from typing import Any, Mapping

import backoff
import pendulum
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.api import API

from .common import JobException, JobTimeoutException, retry_pattern

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
logger = logging.getLogger("airbyte")


class Status(Enum):
    """Async job statuses"""

    COMPLETED = "Job Completed"
    FAILED = "Job Failed"
    SKIPPED = "Job Skipped"
    STARTED = "Job Started"


class AsyncJob:
    """AsyncJob wraps FB AdReport class and provides interface to restart/retry the async job"""

    MAX_WAIT_TO_START = pendulum.duration(minutes=5)
    MAX_WAIT_TO_FINISH = pendulum.duration(minutes=30)

    def __init__(self, api: API, params: Mapping[str, Any]):
        """Initialize

        :param api: Facebook Api wrapper
        :param params: job params, required to start/restart job
        """
        self._params = params
        self._api = api
        self._job = None
        self._start_time = None
        self._finish_time = None
        self._failed = False

    @backoff_policy
    def start(self):
        """Start remote job"""
        if self._job:
            raise RuntimeError(f"{self}: Incorrect usage of start - the job already started, use restart instead")

        self._job = self._api.account.get_insights(params=self._params, is_async=True)
        self._start_time = pendulum.now()
        job_id = self._job["report_run_id"]
        time_range = self._params["time_range"]
        breakdowns = self._params["breakdowns"]
        logger.info(f"Created AdReportRun: {job_id} to sync insights {time_range} with breakdown {breakdowns}")

    def restart(self):
        """Restart failed job"""
        if not self._job or not self.failed:
            raise RuntimeError(f"{self}: Incorrect usage of restart - only failed jobs can be restarted")

        self._job = None
        self._failed = False
        self._start_time = None
        self._finish_time = None
        self.start()
        logger.info(f"{self}: restarted")

    @property
    def elapsed_time(self):
        """Elapsed time since the job start"""
        if not self._start_time:
            return None

        end_time = self._finish_time or pendulum.now()
        return end_time - self._start_time

    @property
    def completed(self) -> bool:
        """Check job status and return True if it is completed successfully

        :return: True if completed successfully, False - if task still running
        :raises: JobException in case job failed to start, failed or timed out
        """
        try:
            return self._check_status()
        except JobException:
            self._failed = True
            raise

    @property
    def failed(self) -> bool:
        """Tell if the job previously failed"""
        return self._failed

    @backoff_policy
    def _update_job(self):
        if not self._job:
            raise RuntimeError(f"{self}: Incorrect usage of the method - the job is not started")
        self._job = self._job.api_get()

    def _check_status(self) -> bool:
        """Perform status check

        :return: True if the job is completed, False - if the job is still running
        :raises: errors if job failed or timed out
        """
        self._update_job()
        job_progress_pct = self._job["async_percent_completion"]
        logger.info(f"{self} is {job_progress_pct}% complete ({self._job['async_status']})")
        runtime = self.elapsed_time

        if self._job["async_status"] == Status.COMPLETED.value:
            self._finish_time = pendulum.now()
            return True
        elif self._job["async_status"] == Status.FAILED.value:
            raise JobException(f"{self._job} failed after {runtime.in_seconds()} seconds.")
        elif self._job["async_status"] == Status.SKIPPED.value:
            raise JobException(f"{self._job} skipped after {runtime.in_seconds()} seconds.")

        if runtime > self.MAX_WAIT_TO_START and self._job["async_percent_completion"] == 0:
            raise JobTimeoutException(
                f"{self._job} did not start after {runtime.in_seconds()} seconds."
                f" This is an intermittent error which may be fixed by retrying the job. Aborting."
            )
        elif runtime > self.MAX_WAIT_TO_FINISH:
            raise JobTimeoutException(
                f"{self._job} did not finish after {runtime.in_seconds()} seconds."
                f" This is an intermittent error which may be fixed by retrying the job. Aborting."
            )
        return False

    @backoff_policy
    def get_result(self) -> Any:
        """Retrieve result of the finished job."""
        if not self._job or self.failed:
            raise RuntimeError(f"{self}: Incorrect usage of get_result - the job is not started of failed")
        return self._job.get_result()

    def __str__(self) -> str:
        """String representation of the job wrapper."""
        job_id = self._job["report_run_id"] if self._job else "<None>"
        time_range = self._params["time_range"]
        breakdowns = self._params["breakdowns"]
        return f"AdReportRun(id={job_id}, time_range={time_range}, breakdowns={breakdowns}"
