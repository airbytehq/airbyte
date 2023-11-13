#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Iterator, List, Mapping, Optional, Type, Union

import backoff
import pendulum
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.objectparser import ObjectParser
from facebook_business.api import FacebookAdsApi, FacebookAdsApiBatch, FacebookBadObjectError, FacebookResponse
from source_facebook_marketing.streams.common import retry_pattern

from ..utils import validate_start_date

logger = logging.getLogger("airbyte")


# `FacebookBadObjectError` occurs in FB SDK when it fetches an inconsistent or corrupted data.
# It still has http status 200 but the object can not be constructed from what was fetched from API.
# Also, it does not happen while making a call to the API, but later - when parsing the result,
# that's why a retry is added to `get_results()` instead of extending the existing retry of `api.call()` with `FacebookBadObjectError`.

backoff_policy = retry_pattern(backoff.expo, FacebookBadObjectError, max_tries=10, factor=5)


def update_in_batch(api: FacebookAdsApi, jobs: List["AsyncJob"]):
    """Update status of each job in the list in a batch, making it most efficient way to update status.

    :param api:
    :param jobs:
    """
    batch = api.new_batch()
    max_batch_size = 50
    for job in jobs:
        # we check it here because job can be already finished
        if len(batch) == max_batch_size:
            while batch:
                # If some of the calls from batch have failed, it returns  a new
                # FacebookAdsApiBatch object with those calls
                batch = batch.execute()
            batch = api.new_batch()
        job.update_job(batch=batch)

    while batch:
        # If some of the calls from batch have failed, it returns  a new
        # FacebookAdsApiBatch object with those calls
        batch = batch.execute()


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

    def __init__(self, api: FacebookAdsApi, interval: pendulum.Period):
        """Init generic async job

        :param api: FB API instance (to create batch, etc)
        :param interval: interval for which the job will fetch data
        """
        self._api = api
        self._interval = interval
        self._attempt_number = 0

    @property
    def interval(self) -> pendulum.Period:
        """Job identifier, in most cases start of the interval"""
        return self._interval

    @abstractmethod
    def start(self):
        """Start remote job"""

    @abstractmethod
    def restart(self):
        """Restart failed job"""

    @property
    def attempt_number(self):
        """Number of attempts"""
        return self._attempt_number

    @property
    @abstractmethod
    def completed(self) -> bool:
        """Check job status and return True if it is completed, use failed/succeeded to check if it was successful"""

    @property
    @abstractmethod
    def failed(self) -> bool:
        """Tell if the job previously failed"""

    @abstractmethod
    def update_job(self, batch: Optional[FacebookAdsApiBatch] = None):
        """Method to retrieve job's status

        :param batch: FB batch executor
        """

    @abstractmethod
    def get_result(self) -> Iterator[Any]:
        """Retrieve result of the finished job."""

    @abstractmethod
    def split_job(self) -> List["AsyncJob"]:
        """Split existing job in few smaller ones"""


class ParentAsyncJob(AsyncJob):
    """Group of async jobs"""

    def __init__(self, jobs: List["InsightAsyncJob"], **kwargs):
        """Initialize jobs"""
        super().__init__(**kwargs)
        self._jobs = jobs

    def start(self):
        """Start each job in the group."""
        for job in self._jobs:
            if job.elapsed_time is None:
                job.start()
        self._attempt_number += 1

    def restart(self):
        """Restart failed jobs"""
        for job in self._jobs:
            if job.failed:
                job.restart()
            self._attempt_number = max(self._attempt_number, job.attempt_number)

    @property
    def completed(self) -> bool:
        """Check job status and return True if all jobs are completed, use failed/succeeded to check if it was successful"""
        return all(job.completed for job in self._jobs)

    @property
    def failed(self) -> bool:
        """Tell if any job previously failed"""
        return any(job.failed for job in self._jobs)

    def update_job(self, batch: Optional[FacebookAdsApiBatch] = None):
        """Checks jobs status in advance."""
        update_in_batch(api=self._api, jobs=self._jobs)

    def get_result(self) -> Iterator[Any]:
        """Retrieve result of the finished job."""
        for job in self._jobs:
            yield from job.get_result()

    def split_job(self) -> List["AsyncJob"]:
        """Split existing job in few smaller ones."""
        new_jobs = []
        for job in self._jobs:
            if job.failed:
                try:
                    new_jobs.extend(job.split_job())
                except ValueError as split_limit_error:
                    logger.error(split_limit_error)
                    logger.info(f'can\'t split "{job}" any smaller, attempting to retry the job.')
                    job.restart()
                    new_jobs.append(job)
            else:
                new_jobs.append(job)
        return new_jobs

    def __str__(self) -> str:
        """String representation of the job wrapper."""
        return f"ParentAsyncJob({self._jobs[0]} ... {len(self._jobs) - 1} jobs more)"


class InsightAsyncJob(AsyncJob):
    """AsyncJob wraps FB AdReport class and provides interface to restart/retry the async job"""

    job_timeout = pendulum.duration(hours=1)
    page_size = 100

    def __init__(self, edge_object: Union[AdAccount, Campaign, AdSet, Ad], params: Mapping[str, Any], **kwargs):
        """Initialize

        :param api: FB API
        :param edge_object: Account, Campaign, AdSet or Ad
        :param params: job params, required to start/restart job
        """
        super().__init__(**kwargs)
        self._params = dict(params)
        self._params["time_range"] = {
            "since": self._interval.start.to_date_string(),
            "until": self._interval.end.to_date_string(),
        }

        self._edge_object = edge_object
        self._job: Optional[AdReportRun] = None
        self._start_time = None
        self._finish_time = None
        self._failed = False

    def split_job(self) -> List["AsyncJob"]:
        """Split existing job in few smaller ones grouped by ParentAsyncJob class."""
        if isinstance(self._edge_object, AdAccount):
            return self._split_by_edge_class(Campaign)
        elif isinstance(self._edge_object, Campaign):
            return self._split_by_edge_class(AdSet)
        elif isinstance(self._edge_object, AdSet):
            return self._split_by_edge_class(Ad)
        raise ValueError("The job is already splitted to the smallest size.")

    def _split_by_edge_class(self, edge_class: Union[Type[Campaign], Type[AdSet], Type[Ad]]) -> List[AsyncJob]:
        """Split insight job by creating insight jobs from lower edge object, i.e.
        Account -> Campaign -> AdSet
        TODO: use some cache to avoid expensive queries across different streams.
        :return: list of new jobs
        """
        if edge_class == Campaign:
            pk_name = "campaign_id"
            level = "campaign"
        elif edge_class == AdSet:
            pk_name = "adset_id"
            level = "adset"
        elif edge_class == Ad:
            pk_name = "ad_id"
            level = "ad"
        else:
            raise RuntimeError("Unsupported edge_class.")  # pragma: no cover

        params = dict(copy.deepcopy(self._params))
        # get objects from attribution window as well (28 day + 1 current day)
        new_start = self._interval.start - pendulum.duration(days=28 + 1)
        new_start = validate_start_date(new_start)
        params["time_range"].update(since=new_start.to_date_string())
        params.update(fields=[pk_name], level=level)
        params.pop("time_increment")  # query all days
        result = self._edge_object.get_insights(params=params)
        ids = set(row[pk_name] for row in result)
        logger.info(f"Got {len(ids)} {pk_name}s for period {self._interval}: {ids}")

        jobs = [InsightAsyncJob(api=self._api, edge_object=edge_class(pk), params=self._params, interval=self._interval) for pk in ids]
        return jobs

    def start(self):
        """Start remote job"""
        if self._job:
            raise RuntimeError(f"{self}: Incorrect usage of start - the job already started, use restart instead")

        self._job = self._edge_object.get_insights(params=self._params, is_async=True)
        self._start_time = pendulum.now()
        self._attempt_number += 1
        logger.info(f"{self}: created AdReportRun")

    def restart(self):
        """Restart failed job"""
        if not self._job or not self.failed:
            raise RuntimeError(f"{self}: Incorrect usage of restart - only failed jobs can be restarted")

        self._job = None
        self._failed = False
        self._start_time = None
        self._finish_time = None
        self.start()
        logger.info(f"{self}: restarted.")

    @property
    def elapsed_time(self) -> Optional[pendulum.duration]:
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
        logger.info(f"{self}: Request failed with response: {response.body()}.")

    def update_job(self, batch: Optional[FacebookAdsApiBatch] = None):
        """Method to retrieve job's status"""
        if not self._job:
            raise RuntimeError(f"{self}: Incorrect usage of the method - the job is not started")

        if self.completed:
            job_status = self._job["async_status"]
            percent = self._job["async_percent_completion"]
            logger.info(f"{self}: is {percent} complete ({job_status})")
            # No need to update job status if its already completed
            return

        if batch is not None:
            self._job.api_get(batch=batch, success=self._batch_success_handler, failure=self._batch_failure_handler)
        else:
            self._job = self._job.api_get()
            self._check_status()

    def _check_status(self) -> bool:
        """Perform status check

        :return: True if the job is completed, False - if the job is still running
        """
        job_status = self._job["async_status"]
        percent = self._job["async_percent_completion"]
        logger.info(f"{self}: is {percent} complete ({job_status})")

        if self.elapsed_time > self.job_timeout:
            logger.info(f"{self}: run more than maximum allowed time {self.job_timeout}.")
            self._finish_time = pendulum.now()
            self._failed = True
            return True
        elif job_status == Status.COMPLETED:
            self._finish_time = pendulum.now()  # TODO: is not actual running time, but interval between check_status calls
            return True
        elif job_status in [Status.FAILED, Status.SKIPPED]:
            self._finish_time = pendulum.now()
            self._failed = True
            logger.info(f"{self}: has status {job_status} after {self.elapsed_time.in_seconds()} seconds.")
            return True

        return False

    @backoff_policy
    def get_result(self) -> Any:
        """Retrieve result of the finished job."""
        if not self._job or self.failed:
            raise RuntimeError(f"{self}: Incorrect usage of get_result - the job is not started or failed")
        return self._job.get_result(params={"limit": self.page_size})

    def __str__(self) -> str:
        """String representation of the job wrapper."""
        job_id = self._job["report_run_id"] if self._job else "<None>"
        breakdowns = self._params["breakdowns"]
        return f"InsightAsyncJob(id={job_id}, {self._edge_object}, time_range={self._interval}, breakdowns={breakdowns})"
