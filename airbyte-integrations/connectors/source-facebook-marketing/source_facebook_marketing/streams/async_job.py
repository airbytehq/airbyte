# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Iterator, List, Mapping, Optional, Type, Union, Tuple

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

# Backoff for SDK parse hiccups
backoff_policy = retry_pattern(backoff.expo, FacebookBadObjectError, max_tries=10, factor=5)

# ----------------------------- batching -------------------------------------
def update_in_batch(api: FacebookAdsApi, jobs: List["AsyncJob"]):
    """
    Efficiently poll many jobs in a single FB batch.
    Parent jobs add their children's calls into this batch.
    """
    batch = api.new_batch()
    max_batch_size = 50

    def flush():
        nonlocal batch
        while batch:
            batch = batch.execute()  # failed calls are returned as a new batch
        batch = api.new_batch()

    for job in jobs:
        if not job.started or job.completed:
            continue
        job.update_job(batch=batch)
        if len(batch) >= max_batch_size:
            flush()

    if batch:
        flush()

# ------------------------------ status --------------------------------------
class Status(str, Enum):
    COMPLETED = "Job Completed"
    FAILED = "Job Failed"
    SKIPPED = "Job Skipped"
    STARTED = "Job Started"
    RUNNING = "Job Running"
    NOT_STARTED = "Job Not Started"

# ------------------------------- base ---------------------------------------
class AsyncJob(ABC):
    """
    Common surface the manager depends on:
      - start(api_limit)
      - update_job(batch)
      - completed / started / failed
      - new_jobs (populated by leaf jobs after splitting)
    """

    def __init__(self, api: FacebookAdsApi, interval: pendulum.Period):
        self._api = api
        self._interval = interval
        self._attempt_number = 0
        self._api_limit = None  # set in start()
        self.new_jobs: List["AsyncJob"] = []

    @property
    def interval(self) -> pendulum.Period:
        return self._interval

    @abstractmethod
    def start(self, api_limit: "APILimit") -> None:
        """Try to start; may no-op if APILimit says no capacity."""

    @property
    @abstractmethod
    def started(self) -> bool:
        """Check if the job has been started"""

    @property
    def attempt_number(self) -> int:
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

# ----------------------------- parent job -----------------------------------
class ParentAsyncJob(AsyncJob):
    """Owns children; started when all children started; completed when all children complete."""

    class _ExportableRow:
        def __init__(self, data: Mapping[str, Any]):
            self._data = dict(data)
        def export_all_data(self) -> Mapping[str, Any]:
            return self._data
        def __getitem__(self, k):
            return self._data[k]
        def __iter__(self):
            return iter(self._data)

    def __init__(self, jobs: List["AsyncJob"], primary_key: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self._primary_key = primary_key or []
        self._jobs: List[AsyncJob] = list(jobs)

    def start(self, api_limit: "APILimit") -> None:
        self._api_limit = api_limit
        for child in self._jobs:
            if not child.started:
                child.start(api_limit)
            if api_limit.limit_reached:
                break
        self._attempt_number += 1

    @property
    def started(self) -> bool:
        return all(child.started for child in self._jobs)

    @property
    def completed(self) -> bool:
        return len(self._jobs) > 0 and all(child.completed for child in self._jobs)

    @property
    def failed(self) -> bool:
        return all(child.completed for child in self._jobs) and any(child.failed for child in self._jobs)

    def update_job(self, batch: Optional[FacebookAdsApiBatch] = None):
        for child in self._jobs:
            if child.started and not child.completed:
                child.update_job(batch=batch)

        # If any child produced replacement work, splice it in-place.
        new_children: List[AsyncJob] = []
        for job in self._jobs:
            if job.new_jobs:
                new_children.extend(job.new_jobs[0]._jobs)
            else:
                new_children.append(job)
        self._jobs = new_children

    def get_result(self) -> Iterator[Any]:
        if not self._primary_key:
            for j in self._jobs:
                yield from j.get_result()
            return

        merged: dict[Tuple[Any, ...], dict] = {}
        print("Merging results by primary key:", self._primary_key, "from", len(self._jobs), "children")
        for child in self._jobs:
            for row in child.get_result():
                data = row.export_all_data() if hasattr(row, "export_all_data") else dict(row)
                key = tuple(data.get(k) for k in self._primary_key)
                if key not in merged:
                    merged[key] = dict(data)
                else:
                    for k, v in data.items():
                        if k in self._primary_key:
                            continue
                        merged[key][k] = v
        print(f"Merged {len(merged)} rows by primary key {merged.keys()}")

        for rec in merged.values():
            yield ParentAsyncJob._ExportableRow(rec)

    def __str__(self) -> str:
        head = self._jobs[0] if self._jobs else "<empty>"
        more = max(0, len(self._jobs) - 1)
        return f"ParentAsyncJob({head} ... {more} jobs more)"

# ------------------------------ leaf job ------------------------------------
class InsightAsyncJob(AsyncJob):
    """Wraps FB AdReportRun with retry/split logic driven in _check_status()."""
    page_size = 100

    def __init__(
        self,
        edge_object: Union[AdAccount, Campaign, AdSet, Ad],
        params: Mapping[str, Any],
        job_timeout: Duration,
        primary_key: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._params = dict(params)
        self._params["time_range"] = {
            "since": self._interval.start.to_date_string(),
            "until": self._interval.end.to_date_string(),
        }
        self._job_timeout = job_timeout
        self._edge_object = edge_object
        self._job: Optional[AdReportRun] = None
        self._primary_key = primary_key or []
        self._start_time = None
        self._finish_time = None
        self._failed = False

    def _log_throttle(self, where: str):
        throttle = getattr(self._api, "ads_insights_throttle", None)
        if throttle:
            logger.info(
                f"{self}: throttle ({where}): per_account={getattr(throttle, 'per_account', 'N/A')}, "
                f"per_application={getattr(throttle, 'per_application', 'N/A')}"
            )

    def start(self, api_limit: "APILimit") -> None:
        self._api_limit = api_limit
        if self.started:
            return
        if not api_limit.try_consume():
            return  # Manager will try again later

        self._job = self._edge_object.get_insights(params=self._params, is_async=True)
        self._start_time = pendulum.now()
        self._attempt_number += 1
        logger.info(f"{self}: created AdReportRun")

    @property
    def started(self) -> bool:
        return self._start_time is not None

    @property
    def elapsed_time(self) -> Optional[pendulum.duration]:
        if not self._start_time:
            return None
        end_time = self._finish_time or pendulum.now()
        return end_time - self._start_time

    @property
    def completed(self) -> bool:
        return self._finish_time is not None

    @property
    def failed(self) -> bool:
        return self._failed

    def update_job(self, batch: Optional[FacebookAdsApiBatch] = None):
        if not self._job:
            return
        if self.completed:
            job_status = self._job.get("async_status")
            percent = self._job.get("async_percent_completion")
            logger.info(f"{self}: is {percent} complete ({job_status})")
            return

        self._job.api_get(
            batch=batch,
            success=self._batch_success_handler,
            failure=self._batch_failure_handler,
        )

    def _batch_success_handler(self, response: FacebookResponse):
        self._job = ObjectParser(reuse_object=self._job).parse_single(response.json())
        self._check_status()

    def _batch_failure_handler(self, response: FacebookResponse):
        logger.info(f"{self}: Request failed with response: {response.body()}.")

    def _check_status(self) -> bool:
        """Advance to terminal state, release capacity, and decide retry/split."""
        job_status = self._job.get("async_status")
        percent = self._job.get("async_percent_completion")
        logger.info(f"{self}: is {percent} complete ({job_status})")

        released = False

        if self.elapsed_time and self.elapsed_time > self._job_timeout:
            logger.info(f"{self}: exceeded max allowed time {self._job_timeout}.")
            self._finish_time = pendulum.now()
            self._failed = True
            released = True
        elif job_status == Status.COMPLETED:
            self._finish_time = pendulum.now()
            released = True
        elif job_status in [Status.FAILED, Status.SKIPPED]:
            self._finish_time = pendulum.now()
            self._failed = True
            logger.info(f"{self}: has status {job_status} after {self.elapsed_time.in_seconds()} seconds.")
            released = True

        print("Job status checked:", self, job_status, percent, "failed:", self._failed, "released:", released)
        if released and self._api_limit:
            self._api_limit.release()

        # Retry/split policy without explicit restart():
        #  - 1st failure → reset state so start() can be called again
        #  - 2nd+ failure → produce replacement jobs via split_job()
        if self._failed:
            if self._attempt_number == 1:
                self._job = None
                self._failed = False
                self._start_time = None
            elif self._attempt_number >= 2:
                self.new_jobs = self.split_job()
            self._finish_time = None

        return self.completed

    # --------------------------- splitting -----------------------------------
    def split_job(self) -> List["AsyncJob"]:
        if isinstance(self._edge_object, AdAccount):
            return self._split_by_edge_class(Campaign)
        elif isinstance(self._edge_object, Campaign):
            return self._split_by_edge_class(AdSet)
        elif isinstance(self._edge_object, AdSet):
            return self._split_by_edge_class(Ad)
        elif isinstance(self._edge_object, Ad):
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
        part_a, part_b = split_candidates[:mid], split_candidates[mid:]

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

    # --------------------------- results -------------------------------------
    @backoff_policy
    def get_result(self) -> Any:
        if not self._job or self.failed:
            raise RuntimeError(f"{self}: Incorrect usage of get_result - the job is not started or failed")
        return self._job.get_result(params={"limit": self.page_size})

    def __str__(self) -> str:
        job_id = self._job["report_run_id"] if self._job else "<None>"
        breakdowns = self._params.get("breakdowns", [])
        return f"InsightAsyncJob(id={job_id}, {self._edge_object}, time_range={self._interval}, breakdowns={breakdowns}, fields={self._params.get('fields', [])})"
