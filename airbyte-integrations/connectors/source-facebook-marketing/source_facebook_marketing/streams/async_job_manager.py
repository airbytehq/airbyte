#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque

import pendulum
from source_facebook_marketing.api import API

from .async_job import AsyncJob


@dataclass
class InsightsAsyncJobManager:
    """
    Class for managing Ads Insights async jobs.
    Responsible for splitting ranges from "from_date" to "to_date", create
    async job DAYS_PER_JOB days long time_range window and schedule jobs
    execution over facebook API /insights call.  Before running next job it
    checks current insight throttle value and if it greater than THROTTLE_LIMIT
    variable, no new jobs added.
    To continue generating new jobs current running jobs should be processed by
    calling "get_next_completed_job" method. It would wait for next job to be
    completed and schedule next async jobs based on current throttle limit.
    Jobs returned by "get_next_completed_job" are ordered by time_range
    parameter.
    """

    # API object to update/get current insights async job throttle limit.
    api: API
    # Start date for async job's time_range parameter. Value is moved forward
    # by DAYS_PER_JOB as new jobs being submitted.
    from_date: pendulum.Date
    # End date for async job's time range. Value is constant.
    to_date: pendulum.Date
    # Params to be passed to <ACCOUNT_ID>/insights request. Will be extended
    # with "time_range" parameter.
    job_params: dict

    logger = logging.getLogger("airbyte")
    _jobs_queue: Deque[AsyncJob] = field(default_factory=deque)

    # When current insights throttle hit this value no new jobs added.
    THROTTLE_LIMIT = 0.7
    FAILED_JOBS_RESTART_COUNT = 5
    # Time to wait before checking job status update again.
    JOB_STATUS_UPDATE_SLEEP_SECONDS = 30
    # Number of days for single date range window.
    DAYS_PER_JOB = 5

    def done(self) -> bool:
        """
        Return True if all jobs have been complete.d
        """
        return len(self._jobs_queue) == 0

    def add_async_jobs(self):
        """
        Enqueue new jobs and shift time range by DAYS_PER_JOB value until
        either throttle limit hit or date range reached "to_date" parameter.
        """
        if self._no_more_ranges():
            return
        self._update_api_throttle_limit()
        prev_jobs_count = len(self._jobs_queue)
        while self._current_throttle() < self.THROTTLE_LIMIT and not self._no_more_ranges():
            next_range = self._get_next_range()
            params = {**self.job_params, **next_range}
            job = AsyncJob(api=self.api, params=params)
            job.start()
            self._jobs_queue.append(job)
        self.logger.info(
            f"Added {len(self._jobs_queue) - prev_jobs_count} jobs. "
            f"Current throttle limit is {self._current_throttle()}, "
            f"{len(self._jobs_queue)} job(s) are running"
        )

    def get_next_completed_job(self) -> AsyncJob:
        """
        Wait until job for next date range is ready and return it. If job
        failed try to restart it for FAILED_JOBS_RESTART_COUNT times. After job
        is completed new jobs added according to current throttling limit.
        Jobs returned by this method are ordered by time_range parameter.
        """
        job = self._jobs_queue[0]
        for _ in range(self.FAILED_JOBS_RESTART_COUNT):
            while not job.completed:
                self.logger.info(f"Job {job} is not ready, wait for {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
                time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)
            if job.failed:
                self.logger.info(f"Job {job} failed, restarting")
                # TODO: wait for insights throttle to go down
                job.restart()
                continue
            self.add_async_jobs()
            return self._jobs_queue.popleft()
        else:
            # TODO: Break range into smaller parts if job failing constantly
            raise Exception(f"Job {job} failed")

    def _current_throttle(self):
        return self.api.api.ads_insights_throttle

    def _get_next_range(self):
        """
        Generate next date range for async job. Shift "from_date" value so it
        represents next job date range start date.
        """
        until = min(
            self.from_date + pendulum.Duration(days=self.DAYS_PER_JOB - 1),
            self.to_date,
        )
        try:
            return {
                "time_range": {
                    "since": self.from_date.to_date_string(),
                    "until": until.to_date_string(),
                },
            }
        finally:
            self.from_date = until.add(days=1)

    def _no_more_ranges(self) -> bool:
        return self.from_date >= self.to_date and not self.done()

    def _update_api_throttle_limit(self):
        """
        Sends <ACCOUNT_ID>/insights GET request with no parameters so it would
        respond with empty list of data so api use "x-fb-ads-insights-throttle"
        header to update current insights throttle limit.
        """
        self.api.account.get_insights()
