#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import time
from typing import Tuple, Iterator, Optional, List, Callable

from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApiBatch
from source_facebook_marketing.api import API

from .async_job import InsightAsyncJob, AsyncJob

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


    TODO:
        check status
        run more if necessary
        get next completed will return any


        jobs that is running        other jobs

        check status of jobs that is running
        restart failed, return completed,
        run more jobs if possible (move jobs from other jobs to runnning jobs)

    """

    # When current insights throttle hit this value no new jobs added.
    THROTTLE_LIMIT = 70
    FAILED_JOBS_RESTART_COUNT = 5
    # Time to wait before checking job status update again.
    JOB_STATUS_UPDATE_SLEEP_SECONDS = 30
    # Maximum of concurrent jobs that could be scheduled. Since throttling
    # limit is not reliable indicator of async workload capability we still
    # have to use this parameter. It is equal to maximum number of request in batch (FB API limit)
    MAX_JOBS_IN_QUEUE = 100
    MAX_JOBS_TO_CHECK = 50

    def __init__(self, api: API, get_campaigns_for_period: Callable, jobs: Iterator[AsyncJob]):
        """
        get list of jobs
        run window
        check status of jobs in batch

        :param jobs:
        """
        self._api = api
        self._get_campaigns_for_period = get_campaigns_for_period
        self._jobs = jobs
        self._running_jobs = []
        self._empty = False

    @property
    def done(self):
        return self._empty

    def start_jobs(self):
        """Enqueue new jobs."""

        self._update_api_throttle_limit()
        self._wait_throttle_limit_down()
        prev_jobs_count = len(self._running_jobs)
        while (
            self._get_current_throttle_value() < self.THROTTLE_LIMIT
            and len(self._running_jobs) < self.MAX_JOBS_IN_QUEUE
        ):
            job = next(self._jobs, None)
            if not job:
                self._empty = True
                break
            job.start()
            self._running_jobs.append(job)

        logger.info(
            f"Added: {len(self._running_jobs) - prev_jobs_count} jobs. "
            f"Current throttle limit is {self._current_throttle()}, "
            f"{len(self._running_jobs)}/{self.MAX_JOBS_IN_QUEUE} job(s) in queue"
        )

    def completed_jobs(self) -> Iterator[AsyncJob]:
        """ Wait until job is ready and return it. If job
            failed try to restart it for FAILED_JOBS_RESTART_COUNT times. After job
            is completed new jobs added according to current throttling limit.

        :yield: completed jobs
        """
        if not self._running_jobs:
            self.start_jobs()

        while self._running_jobs:
            completed_jobs = self._check_jobs_status_and_restart()
            while not completed_jobs:
                logger.info(f"No jobs ready to be consumed, wait for {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
                time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)
                completed_jobs = self._check_jobs_status_and_restart()
                yield from completed_jobs

            self.start_jobs()

    def _check_jobs_status_and_restart(self) -> List[AsyncJob]:
        """ Checks jobs status in advance and restart if some failed.

        :return: list of completed jobs
        """
        completed_jobs = []
        running_jobs = []

        api_batch: FacebookAdsApiBatch = self._api.api.new_batch()
        for job in self._running_jobs:
            # we check it here because job can be an instance of ParentAsyncJob, which uses its own batch object
            if len(api_batch) >= self.MAX_JOBS_TO_CHECK:
                logger.info("Reached batch queue limit")
                break
            job.update_job(batch=api_batch)

        while api_batch:
            # If some of the calls from batch have failed, it returns  a new
            # FacebookAdsApiBatch object with those calls
            api_batch = api_batch.execute()

        failed_num = 0
        self._wait_throttle_limit_down()
        for job in self._running_jobs:
            if job.completed:
                if job.failed:
                    if job.restart_number >= self.FAILED_JOBS_RESTART_COUNT:
                        raise Exception(f"Job {job} failed more than {self.FAILED_JOBS_RESTART_COUNT} times. Terminating...")
                    elif job.restart_number:
                        logger.info(f"Job {job} failed, trying to split job into smaller chunks (campaigns).")
                        group_job = job.split_job()
                        running_jobs.append(group_job)
                        group_job.start()
                    else:
                        logger.info(f"Job {job} failed, restarting")
                        job.restart()
                        running_jobs.append(job)
                    failed_num += 1
                else:
                    completed_jobs.append(job)
            else:
                running_jobs.append(job)

        self._running_jobs = running_jobs
        logger.info(f"Completed jobs: {len(completed_jobs)}, Failed jobs: {failed_num}, Running jobs: {len(self._running_jobs)}")

        return completed_jobs

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
