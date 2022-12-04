#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import time
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
    THROTTLE_LIMIT = 70
    MAX_NUMBER_OF_ATTEMPTS = 20
    # Time to wait before checking job status update again.
    JOB_STATUS_UPDATE_SLEEP_SECONDS = 30
    # Maximum of concurrent jobs that could be scheduled. Since throttling
    # limit is not reliable indicator of async workload capability we still have to use this parameter.
    MAX_JOBS_IN_QUEUE = 100

    def __init__(self, api: "API", jobs: Iterator[AsyncJob]):
        """Init

        :param api:
        :param jobs:
        """
        self._api = api
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
            job.start()
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
                if isinstance(job, ParentAsyncJob):
                    # if this job is a ParentAsyncJob, it holds X number of jobs
                    # we want to check that none of these nested jobs have exceeded MAX_NUMBER_OF_ATTEMPTS
                    for nested_job in job._jobs:
                        if nested_job.attempt_number >= self.MAX_NUMBER_OF_ATTEMPTS:
                            raise JobException(f"{nested_job}: failed more than {self.MAX_NUMBER_OF_ATTEMPTS} times. Terminating...")
                if job.attempt_number >= self.MAX_NUMBER_OF_ATTEMPTS:
                    raise JobException(f"{job}: failed more than {self.MAX_NUMBER_OF_ATTEMPTS} times. Terminating...")
                elif job.attempt_number == 2:
                    logger.info("%s: failed second time, trying to split job into smaller jobs.", job)
                    smaller_jobs = job.split_job()
                    grouped_jobs = ParentAsyncJob(api=self._api.api, jobs=smaller_jobs, interval=job.interval)
                    running_jobs.append(grouped_jobs)
                    grouped_jobs.start()
                else:
                    logger.info("%s: failed, restarting", job)
                    job.restart()
                    running_jobs.append(job)
                failed_num += 1
            elif job.completed:
                completed_jobs.append(job)
            else:
                running_jobs.append(job)

        self._running_jobs = running_jobs
        logger.info(f"Completed jobs: {len(completed_jobs)}, Failed jobs: {failed_num}, Running jobs: {len(self._running_jobs)}")

        return completed_jobs

    def _wait_throttle_limit_down(self):
        while self._get_current_throttle_value() > self.THROTTLE_LIMIT:
            logger.info(f"Current throttle is {self._api.api.ads_insights_throttle}, wait {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
            time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)
            self._update_api_throttle_limit()

    def _get_current_throttle_value(self) -> float:
        """
        Get current ads insights throttle value based on app id and account id.
        It evaluated as minimum of those numbers cause when account id throttle
        hit 100 it cool down very slowly (i.e. it still says 100 despite no jobs
        running and it capable serve new requests). Because of this behaviour
        facebook throttle limit is not reliable metric to estimate async workload.
        """
        throttle = self._api.api.ads_insights_throttle

        return min(throttle.per_account, throttle.per_application)

    def _update_api_throttle_limit(self):
        """
        Sends <ACCOUNT_ID>/insights GET request with no parameters so it would
        respond with empty list of data so api use "x-fb-ads-insights-throttle"
        header to update current insights throttle limit.
        """
        self._api.account.get_insights()
