#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import itertools
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Mapping, Optional, List

import backoff
import pendulum
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.adobjects.objectparser import ObjectParser
from facebook_business.api import FacebookResponse, FacebookAdsApiBatch
from facebook_business.exceptions import FacebookRequestError

from .common import retry_pattern

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
logger = logging.getLogger("airbyte")


class Status(str, Enum):
    """Async job statuses"""

    COMPLETED = "Job Completed"
    FAILED = "Job Failed"
    SKIPPED = "Job Skipped"
    STARTED = "Job Started"
    RUNNING = "Job Running"
    NOT_STARTED = "Job Not Started"


class AsyncJob(ABC):
    """Abstract AsyncJob base class"""

    @abstractmethod
    def start(self):
        """Start remote job"""

    @abstractmethod
    def restart(self):
        """Restart failed job"""

    @property
    @abstractmethod
    def completed(self) -> bool:
        """Check job status and return True if it is completed, use failed/succeeded to check if it was successful"""

    @property
    @abstractmethod
    def failed(self) -> bool:
        """Tell if the job previously failed"""

    @abstractmethod
    def update_job(self, batch = None):
        """Method to retrieve job's status, separated because of retry handler"""

    @abstractmethod
    def get_result(self) -> Any:
        """Retrieve result of the finished job."""


class ParentAsyncJob(AsyncJob):
    def __init__(self, jobs: List[AsyncJob]):
        self._jobs = jobs

    def start(self):
        """Start remote job"""
        for job in self._jobs:
            job.start()

    def restart(self):
        """Restart failed job"""
        for job in self._jobs:
            job.restart()

    @property
    def completed(self) -> bool:
        """Check job status and return True if all jobs are completed, use failed/succeeded to check if it was successful"""
        return all(job.completed for job in self._jobs)

    @property
    def failed(self) -> bool:
        """Tell if any job previously failed"""
        return any(job.failed for job in self._jobs)

    def update_job(self, batch=None):
        """Checks jobs status in advance and restart if some failed."""
        for job in self._jobs:
            job.update_job(batch=batch)

        while batch:
            # If some of the calls from batch have failed, it returns  a new
            # FacebookAdsApiBatch object with those calls
            batch = batch.execute()

    def get_result(self) -> Any:
        """Retrieve result of the finished job."""
        for job in self._jobs:
            yield from job.get_result()


class InsightAsyncJob(AsyncJob):
    """AsyncJob wraps FB AdReport class and provides interface to restart/retry the async job"""

    def __init__(self, edge_object: Any, params: Mapping[str, Any]):
        """Initialize

        :param edge_object: Account, Campaign, AdSet or Ad
        :param params: job params, required to start/restart job
        """
        self._params = params
        self._edge_object = edge_object
        self._job: Optional[AdReportRun] = None
        self._start_time = None
        self._finish_time = None
        self._failed = False

    @backoff_policy
    def start(self):
        """Start remote job"""
        if self._job:
            raise RuntimeError(f"{self}: Incorrect usage of start - the job already started, use restart instead")

        self._job = self._edge_object.get_insights(params=self._params, is_async=True)
        self._start_time = pendulum.now()
        job_id = self._job["report_run_id"]
        time_range = self._params["time_range"]
        breakdowns = self._params["breakdowns"]
        logger.info(f"Created AdReportRun: {job_id} to sync insights {time_range} with breakdown {breakdowns} for {self._edge_object}")

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
        """Check job status and return True if it is completed, use failed/succeeded to check if it was successful

        :return: True if completed, False - if task still running
        :raises: JobException in case job failed to start, failed or timed out
        """
        return bool(self._finish_time is not None)

    @property
    def failed(self) -> bool:
        """Tell if the job previously failed"""
        return self._failed

    def _batch_success_handler(self, response: FacebookResponse):
        """Update job status from response"""
        self._job = ObjectParser(reuse_object=self._job).parse_single(response.json())
        self._check_status()

    def _batch_failure_handler(self, response: FacebookResponse):
        """Update job status from response"""
        logger.info(f"Request failed with response: {response.body()}")

    @backoff_policy
    def update_job(self, batch = None):
        """Method to retrieve job's status, separated because of retry handler"""
        if not self._job:
            raise RuntimeError(f"{self}: Incorrect usage of the method - the job is not started")

        if self.completed:
            job_progress_pct = self._job["async_percent_completion"]
            logger.info(f"{self} is {job_progress_pct}% complete ({self._job['async_status']})")
            # No need to update job status if its already completed
            return

        if batch:
            request = self._job.api_get(pending=True)
            batch.add_request(request, success=self._batch_success_handler, failure=self._batch_failure_handler)
        else:
            self._job = self._job.api_get()
            self._check_status()

    def _check_status(self) -> bool:
        """Perform status check

        :return: True if the job is completed, False - if the job is still running
        """
        job_progress_pct = self._job["async_percent_completion"]
        job_status = self._job["async_status"]
        logger.info(f"{self} is {job_progress_pct}% complete ({job_status})")

        if job_status == Status.COMPLETED:
            self._finish_time = pendulum.now()  # TODO: is not actual running time, but interval between check_status calls
            return True
        elif job_status in [Status.FAILED, Status.SKIPPED]:
            self._finish_time = pendulum.now()
            self._failed = True
            logger.info(f"{self._job} has status {job_status} after {self.elapsed_time.in_seconds()} seconds.")
            return True

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
        return f"AdReportRun(id={job_id}, {self._edge_object}, time_range={time_range}, breakdowns={breakdowns}"
