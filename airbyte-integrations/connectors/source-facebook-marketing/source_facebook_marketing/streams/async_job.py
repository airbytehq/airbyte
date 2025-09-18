#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from abc import ABC, abstractmethod
from enum import Enum
import time
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
from pendulum.duration import Duration

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
    def start(self, capacity:int) -> int:
        """Start remote job. Returns capacity used by the job"""

    @property
    @abstractmethod
    def started(self) -> bool:
        """Check if the job has been started"""

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

    @abstractmethod
    def restart_or_split(self):
        """Restart failed job or split it if it can't be restarted"""


class ParentAsyncJob(AsyncJob):
    """Group of async jobs"""

    def __init__(self, jobs: List["InsightAsyncJob"], primary_key = Optional[List[str]], **kwargs):
        """Initialize jobs"""
        super().__init__(**kwargs)
        self._primary_key = primary_key
        self._jobs = jobs

    def start(self, capacity) -> int:
        """Start each job in the group."""
        used_capacity = 0
        for job in self._jobs:
            if job.elapsed_time is None:
                job.start(1)
                used_capacity += 1
            if used_capacity >= capacity:
                break

        self._attempt_number += 1
        return capacity - used_capacity

    @property
    def started(self) -> bool:
        return all([job.started for job in self._jobs])

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
        update_in_batch(api=self._api, jobs=[job for job in self._jobs if job.started and not job.completed])

    def get_result(self) -> Iterator[Any]:
        """
        Retrieve merged results from children.
        - If primary_key is empty, stream children results as-is (fallback).
        - Otherwise, merge rows with the same PK tuple; later fields overwrite earlier ones.
        """
        if not self._primary_key:
            # Fallback: no merge key provided -> stream-through
            for j in self._jobs:
                yield from j.get_result()
            return

        merged: dict[tuple, dict] = {}

        for child in self._jobs:
            for row in child.get_result():
                # FB SDK “row” usually has export_all_data(); handle plain dicts too.
                data = row.export_all_data() if hasattr(row, "export_all_data") else dict(row)
                key = tuple(data.get(k) for k in self._primary_key)

                if key not in merged:
                    merged[key] = dict(data)  # first occurrence initializes the bucket
                else:
                    # Merge non-PK fields; PK columns keep their original values.
                    for k, v in data.items():
                        if k in self._primary_key:
                            continue
                        merged[key][k] = v

        # Yield rows compatible with downstream `.export_all_data()` access
        for rec in merged.values():
            yield self._ExportableRow(rec)

    def split_job(self) -> List["AsyncJob"]:
        """Split existing job in few smaller ones."""
        new_jobs = []
        for job in self._jobs:
            if job.failed:
                self._jobs.extend(job.split_job()._jobs)
        return [self]

    def restart_or_split(self) -> tuple[List["AsyncJob"], List["AsyncJob"]]:
        """
        Repair/replace only failed children:
          - For each failed child, call its restart_or_split()
          - Replace that child with the returned 'running' child jobs
          - Enqueue any 'queued' child jobs for the manager
        Return:
          ([self], queued_children)
        We keep the SAME ParentAsyncJob instance in the running set; the manager stays parent-agnostic.
        """
        new_children: List[AsyncJob] = []

        for child in self._jobs:
            if child.failed:
                running_kids, queued_kids = child.restart_or_split()
                if queued_kids:
                    # Job is splitted into multiple smaller jobs
                    new_children.extend(running_kids[0]._jobs)
                else:
                    # Job is restarted (single child)
                    new_children.append(running_kids[0])
            else:
                # Keep non-failed children (completed or still running)
                new_children.append(child)

        self._jobs = new_children
        # Important: do NOT start anything here. The manager will start queued children later.
        return [self], [] if self.started else [self]

    def __str__(self) -> str:
        """String representation of the job wrapper."""
        return f"ParentAsyncJob({self._jobs[0]} ... {len(self._jobs) - 1} jobs more)"


class InsightAsyncJob(AsyncJob):
    """AsyncJob wraps FB AdReport class and provides interface to restart/retry the async job"""

    page_size = 100

    def __init__(
        self,
        edge_object: Union[AdAccount, Campaign, AdSet, Ad],
        params: Mapping[str, Any],
        job_timeout: Duration,
        primary_key: Optional[str] = None,
        **kwargs,
    ):
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
        self._job_timeout = job_timeout

        self._edge_object = edge_object
        self._job: Optional[AdReportRun] = None
        self._primary_key = primary_key
        self._start_time = None
        self._finish_time = None
        self._failed = False

    def _log_throttle(self, where: str):
        """
        Just log the current throttle values for debugging/monitoring.
        """
        throttle = getattr(self._api, "ads_insights_throttle", None)
        if throttle:
            logger.info(
                f"{self}: throttle check ({where}): "
                f"per_account={getattr(throttle, 'per_account', 'N/A')}, "
                f"per_application={getattr(throttle, 'per_application', 'N/A')}"
            )
        else:
            logger.info(f"{self}: throttle check ({where}): no throttle info available")

    @property
    def started(self) -> bool:
        return self._start_time is not None

    def restart_or_split(self):
        if self.attempt_number == 1:
            logger.info(
                "%s: failed second time, trying to split job into smaller jobs.",
                self,
            )
            smaller_jobs = self.split_job()
            if len(smaller_jobs) == 1:
                smaller_jobs[0].start(1)
                if isinstance(smaller_jobs[0], ParentAsyncJob):
                    return smaller_jobs, smaller_jobs
                else:
                    return smaller_jobs, []
            else:
                # job is splitted into multiple smaller jobs
                smaller_jobs[0].start(1)
                return [smaller_jobs[0]], smaller_jobs[1:]
        else:
            logger.info("%s: failed, restarting", self)
            self.restart()
            return self, []

    def split_job(self) -> List["AsyncJob"]:
        if isinstance(self._edge_object, AdAccount):
            return self._split_by_edge_class(Campaign)
        elif isinstance(self._edge_object, Campaign):
            return self._split_by_edge_class(AdSet)
        elif isinstance(self._edge_object, AdSet):
            return self._split_by_edge_class(Ad)
        elif isinstance(self._edge_object, Ad):
            # Ad-level → split by fields → return a single ParentAsyncJob that will merge
            return [self._split_by_fields_parent()]
        else:
            raise ValueError("Unsupported edge for splitting")

    def _split_by_edge_class(self, edge_class: Union[Type[Campaign], Type[AdSet], Type[Ad]]) -> List["AsyncJob"]:
        if edge_class == Campaign:
            pk_name, level = "campaign_id", "campaign"
        elif edge_class == AdSet:
            pk_name, level = "adset_id", "adset"
        elif edge_class == Ad:
            pk_name, level = "ad_id", "ad"
        else:
            raise RuntimeError("Unsupported edge_class")

        since = validate_start_date(self._interval.start - pendulum.duration(days=29))
        params = {
            "fields": [pk_name],
            "level": level,
            "time_range": {"since": since.to_date_string(), "until": self._interval.end.to_date_string()},
        }

        try:
            id_job: AdReportRun = self._edge_object.get_insights(params=params, is_async=True)
        except Exception as e:
            raise ValueError(f"Failed to start ID-collection at level={level}: {e}") from e

        start_ts = pendulum.now()
        while True:
            id_job = id_job.api_get()
            status = id_job.get("async_status")
            percent = id_job.get("async_percent_completion")
            logger.info(f"[Split:{level}] status={status}, {percent}%")
            if status == Status.COMPLETED:
                break
            if status in (Status.FAILED, Status.SKIPPED):
                raise ValueError(f"ID-collection failed for level={level}: {status}")
            if (pendulum.now() - start_ts) > self._job_timeout:
                raise ValueError(f"ID-collection timed out for level={level}")
            time.sleep(30)

        try:
            result_cursor = id_job.get_result(params={"limit": self.page_size})
        except FacebookBadObjectError as e:
            raise ValueError(f"Failed to fetch ID-collection results for level={level}: {e}") from e

        ids = {row[pk_name] for row in result_cursor if pk_name in row}
        logger.info(f"[Split:{level}] collected {len(ids)} {pk_name}(s)")

        jobs: List[AsyncJob] = [
            InsightAsyncJob(
                api=self._api,
                edge_object=edge_class(pk),
                params=self._params,
                interval=self._interval,
                job_timeout=self._job_timeout,
                primary_key=self._primary_key,
            )
            for pk in ids
        ]
        if not jobs:
            raise ValueError(f"No child IDs at level={level}")
        return jobs

    def _split_by_fields_parent(self) -> ParentAsyncJob:
        all_fields: List[str] = list(self._params.get("fields", []))

        split_candidates = [f for f in all_fields if f not in self._primary_key]
        if len(split_candidates) <= 1:
            raise ValueError("Cannot split by fields: not enough non-PK fields")

        mid = len(split_candidates) // 2
        part_a = split_candidates[:mid]
        part_b = split_candidates[mid:]

        params_a = dict(self._params); params_a["fields"] = self._primary_key + part_a
        params_b = dict(self._params); params_b["fields"] = self._primary_key + part_b

        job_a = InsightAsyncJob(
            api=self._api,
            edge_object=self._edge_object,
            params=params_a,
            interval=self._interval,
            job_timeout=self._job_timeout,
            primary_key=self._primary_key,
        )
        job_b = InsightAsyncJob(
            api=self._api,
            edge_object=self._edge_object,
            params=params_b,
            interval=self._interval,
            job_timeout=self._job_timeout,
            primary_key=self._primary_key,
        )
        logger.info("%s split by fields: common=%d, A=%d, B=%d", self, len(self._primary_key), len(part_a), len(part_b))
        return ParentAsyncJob(jobs=[job_a, job_b], api=self._api, interval=self._interval, primary_key=self._primary_key)

    def start(self, capacity:int) -> int:
        """Start remote job"""
        if self._job:
            raise RuntimeError(f"{self}: Incorrect usage of start - the job already started, use restart instead")

        self._job = self._edge_object.get_insights(params=self._params, is_async=True)
        self._start_time = pendulum.now()
        self._attempt_number += 1
        logger.info(f"{self}: created AdReportRun")
        return 1

    def restart(self):
        """Restart failed job"""
        if not self._job or not self.failed:
            raise RuntimeError(f"{self}: Incorrect usage of restart - only failed jobs can be restarted")

        self._job = None
        self._failed = False
        self._start_time = None
        self._finish_time = None
        self.start(1)
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
            self._job.api_get(
                batch=batch,
                success=self._batch_success_handler,
                failure=self._batch_failure_handler,
            )
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

        if self.elapsed_time > self._job_timeout:
            logger.info(f"{self}: run more than maximum allowed time {self._job_timeout}.")
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
        return f"InsightAsyncJob(id={job_id}, {self._edge_object}, time_range={self._interval}, breakdowns={breakdowns}, fields={self._params.get('fields', [])})"
