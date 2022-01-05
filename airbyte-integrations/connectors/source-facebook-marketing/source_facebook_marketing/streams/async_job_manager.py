#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import itertools
import logging
import time
from collections import deque
from typing import Tuple, List

from facebook_business.api import FacebookAdsApiBatch
from source_facebook_marketing.api import API

from .async_job import InsightAsyncJob


logger = logging.getLogger("airbyte")


class InsightAsyncJobManager:
    """
    Class for managing Ads Insights async jobs.
    Responsible for splitting ranges from "from_date" to "to_date", create
    async job DAYS_PER_JOB days long time_range window and schedule jobs
    execution over facebook API /insights call.  Before running next job it
    checks current insight throttle value and if it greater than THROTTLE_LIMIT
    variable, no new jobs added.
    To continue generating new jobs current running jobs should be processed by
    calling "get_next_completed_job" method.
    Jobs returned by "get_next_completed_job" are ordered by time_range
    parameter.
    """

    # When current insights throttle hit this value no new jobs added.
    THROTTLE_LIMIT = 70
    FAILED_JOBS_RESTART_COUNT = 5
    # Time to wait before checking job status update again.
    JOB_STATUS_UPDATE_SLEEP_SECONDS = 30
    # Maximum of concurrent jobs that could be scheduled. Since throttling
    # limit is not reliable indicator of async workload capability we still
    # have to use this parameter.
    MAX_JOBS_IN_QUEUE = 50

    def __init__(self, api:API, jobs: List[InsightAsyncJob]):
        """
        get list of jobs
        run window
        check status of jobs in batch

        :param jobs:
        """
        self._api = api
        self._jobs = deque(jobs)
        self._jobs_queue = deque()

    def wait_for_completion(self):
        while self._jobs or self._jobs_queue:
            self.get_next_completed_job()

    def start_jobs(self):
        """
        Enqueue new jobs and shift time range by DAYS_PER_JOB value until
        either throttle limit hit or date range reached "to_date" parameter.
        """
        self._update_api_throttle_limit()
        self._wait_throttle_limit_down()
        prev_jobs_count = len(self._jobs_queue)
        completed_jobs_count = sum(job.completed for job in self._jobs_queue)
        while (
            self._get_current_throttle_value() < self.THROTTLE_LIMIT
            and len(self._jobs_queue) - completed_jobs_count < self.MAX_JOBS_IN_QUEUE
            and self._jobs
        ):
            job = self._jobs.popleft()
            job.start()
            self._jobs_queue.append(job)

        logger.info(
            f"Completed: {completed_jobs_count} jobs. "
            f"Running: {prev_jobs_count - completed_jobs_count} jobs. "
            f"Added: {len(self._jobs_queue) - prev_jobs_count} jobs. "
            f"Current throttle limit is {self._current_throttle()}, "
            f"{len(self._jobs_queue)} job(s) are running"
        )

    def get_next_completed_job(self) -> InsightAsyncJob:
        """
        Wait until job for next date range is ready and return it. If job
        failed try to restart it for FAILED_JOBS_RESTART_COUNT times. After job
        is completed new jobs added according to current throttling limit.
        Jobs returned by this method are ordered by time_range parameter.
        """
        if not self._jobs_queue:
            self.start_jobs()

        job = self._jobs_queue[0]
        for _ in range(self.FAILED_JOBS_RESTART_COUNT):
            self._check_jobs_status_and_restart()
            while not job.completed:
                logger.info(f"Job {job} is not ready, wait for {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
                time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)
                self._check_jobs_status_and_restart()

            if job.failed:
                logger.info(f"Job {job} failed, restarting")
                self._wait_throttle_limit_down()
                job.restart()
            else:
                self._jobs_queue.popleft()
                self.start_jobs()
                return job
        else:
            raise Exception(f"Job {job} failed")

    def _check_jobs_status_and_restart(self):
        """
        Checks jobs status in advance and restart if some failed.
        """

        api_batch: FacebookAdsApiBatch = self._api.api.new_batch()
        for job in itertools.islice(self._jobs_queue, 0, self.MAX_JOBS_IN_QUEUE):
            job.update_job(batch=api_batch)

        while api_batch:
            # If some of the calls from batch have failed, it returns  a new
            # FacebookAdsApiBatch object with those calls
            api_batch = api_batch.execute()

        for job in itertools.islice(self._jobs_queue, 1, self.MAX_JOBS_IN_QUEUE):
            if job.failed:
                job.restart()

    def _wait_throttle_limit_down(self):
        while self._get_current_throttle_value() > self.THROTTLE_LIMIT:
            logger.info(f"Current throttle is {self._current_throttle()}, wait {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
            time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)
            self._update_api_throttle_limit()

    def _current_throttle(self) -> Tuple[float, float]:
        """
        Return tuple of 2 floats representing current ads insights throttle values for app id and account id
        """
        return self._api.api.ads_insights_throttle

    def _get_current_throttle_value(self) -> float:
        """
        Get current ads insights throttle value based on app id and account id.
        It evaluated as minimum of those numbers cause when account id throttle
        hit 100 it cool down very slowly (i.e. it still says 100 despite no jobs
        running and it capable serve new requests). Because of this behaviour
        facebook throttle limit is not reliable metric to estimate async workload.
        """
        return min(self._current_throttle()[0], self._current_throttle()[1])

    def _update_api_throttle_limit(self):
        """
        Sends <ACCOUNT_ID>/insights GET request with no parameters so it would
        respond with empty list of data so api use "x-fb-ads-insights-throttle"
        header to update current insights throttle limit.
        """
        self._api.account.get_insights()
