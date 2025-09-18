#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from itertools import chain
from typing import TYPE_CHECKING, Iterator, List

from source_facebook_marketing.streams.common import JobException

from .async_job import AsyncJob, ParentAsyncJob, update_in_batch


if TYPE_CHECKING:  # pragma: no cover
    from source_facebook_marketing.api import API

logger = logging.getLogger("airbyte")


class InsightAsyncJobManager:
    """
    Class for managing Ads Insights async jobs. Before running next job it
    checks current insight throttle value and if it greater than THROTTLE_LIMIT variable, no new jobs added.
    To consume completed jobs use completed_job generator, jobs will be returned in the order they finished.
    """

    # When current insights throttle hit this value no new jobs added.
    THROTTLE_LIMIT = 90
    MAX_NUMBER_OF_ATTEMPTS = 20
    # Time to wait before checking job status update again.
    JOB_STATUS_UPDATE_SLEEP_SECONDS = 30
    # Maximum of concurrent jobs that could be scheduled. Since throttling
    # limit is not reliable indicator of async workload capability we still have to use this parameter.
    MAX_JOBS_IN_QUEUE = 100

    def __init__(self, api: "API", jobs: Iterator[AsyncJob], account_id: str):
        """Init

        :param api:
        :param jobs:
        """
        self._api = api
        self._account_id = account_id
        self._jobs = iter(jobs)
        self._running_jobs = []

    def _start_jobs(self):
        """Enqueue new jobs."""

        self._update_api_throttle_limit()
        self._wait_throttle_limit_down()
        prev_jobs_count = len(self._running_jobs)
        while self._get_current_throttle_value() < self.THROTTLE_LIMIT and len(self._running_jobs) < self.MAX_JOBS_IN_QUEUE:
            job = next(self._jobs, None)
            if not job:
                self._empty = True
                break
            job.start(1)
            if not job.started:
                self._jobs = iter(chain([job], self._jobs))

            self._running_jobs.append(job)

        logger.info(
            f"Added: {len(self._running_jobs) - prev_jobs_count} jobs. "
            f"Current throttle limit is {self._api.api.ads_insights_throttle}, "
            f"{len(self._running_jobs)}/{self.MAX_JOBS_IN_QUEUE} job(s) in queue"
        )

    def completed_jobs(self) -> Iterator[AsyncJob]:
        """Wait until job is ready and return it. If job
            failed try to restart it for FAILED_JOBS_RESTART_COUNT times. After job
            is completed new jobs added according to current throttling limit.

        :yield: completed jobs
        """
        if not self._running_jobs:
            self._start_jobs()

        while self._running_jobs:
            completed_jobs = self._check_jobs_status_and_restart()
            while not completed_jobs:
                logger.info(f"No jobs ready to be consumed, wait for {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
                time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)
                completed_jobs = self._check_jobs_status_and_restart()
            yield from completed_jobs
            self._start_jobs()

    def _check_jobs_status_and_restart(self) -> List[AsyncJob]:
        """Checks jobs status in advance and restart if some failed.

        :return: list of completed jobs
        """
        completed_jobs = []
        running_jobs = []
        failed_num = 0

        update_in_batch(api=self._api.api, jobs=self._running_jobs)
        self._wait_throttle_limit_down()
        for job in self._running_jobs:
            if job.failed:
                running_job, queued_jobs = job.restart_or_split()
                running_jobs.extend(running_job)
                self._jobs = iter(chain(queued_jobs, self._jobs))
            elif job.completed:
                completed_jobs.append(job)
            else:
                running_jobs.append(job)

        self._running_jobs = running_jobs
        logger.info(f"Completed jobs: {len(completed_jobs)}, Failed jobs: {failed_num}, Running jobs: {len(self._running_jobs)}")

        return completed_jobs

    def _wait_throttle_limit_down(self):
        current_throttle = self._get_current_throttle_value()
        print(f"Current throttle is {current_throttle} and limit is {self.THROTTLE_LIMIT}")
        while current_throttle > self.THROTTLE_LIMIT:
            logger.info(f"Current throttle is {self._api.api.ads_insights_throttle}, wait {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
            time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)
            self._update_api_throttle_limit()

    def _get_current_throttle_value(self) -> float:
        """
        Get current ads insights throttle value based on app id and account id.
        It evaluated as minimum of those numbers cause when account id throttle
        hit 100 it cools down very slowly (i.e. it still says 100 despite no jobs
        running and it capable serve new requests). Because of this behaviour
        facebook throttle limit is not reliable metric to estimate async workload.
        """
        throttle = self._api.api.ads_insights_throttle

        return max(throttle.per_account, throttle.per_application)

    def _update_api_throttle_limit(self):
        """
        Sends <ACCOUNT_ID>/insights GET request with no parameters, so it would
        respond with empty list of data so api use "x-fb-ads-insights-throttle"
        header to update current insights throttle limit.
        """
        self._api.get_account(account_id=self._account_id).get_insights()
