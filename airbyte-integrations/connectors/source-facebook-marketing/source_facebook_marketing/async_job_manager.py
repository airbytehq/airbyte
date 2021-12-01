#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import time
from collections import deque
from dataclasses import dataclass, field

import pendulum
from source_facebook_marketing.api import API

from .async_job import AsyncJob


@dataclass
class InsightsAsyncJobManager:

    api: API
    from_date: pendulum.Date
    to_date: pendulum.Date
    start_days_per_job: int
    job_params: dict

    logger = logging.getLogger("airbyte")
    _jobs_queue: deque = field(default_factory=deque)

    THROTTLE_LIMIT = 0.7
    FAILED_JOBS_RESTART_COUNT = 5
    JOB_STATUS_UPDATE_SLEEP_SECONDS = 30

    def done(self) -> bool:
        """docstring for done"""
        return len(self._jobs_queue) == 0

    def _current_throttle(self):
        return self.api.api.ads_insights_throttle

    def get_next_range(self):
        until = min(
            self.from_date + pendulum.Duration(days=self.start_days_per_job - 1),
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

    def no_more_ranges(self) -> bool:
        return self.from_date >= self.to_date and not self.done()

    def add_async_jobs(self):
        if self.no_more_ranges():
            return
        self._update_api_throttle_limit()
        while self._current_throttle() < self.THROTTLE_LIMIT and not self.no_more_ranges():
            next_range = self.get_next_range()
            params = {**self.job_params, **next_range}
            job = AsyncJob(api=self.api, params=params)
            job.start()
            self._jobs_queue.append(job)
        self.logger.info(f"Current throttle limit is {self._current_throttle()}, {len(self._jobs_queue)} job(s) are running")

    def get_next_completed_job(self) -> AsyncJob:
        job = self._jobs_queue[0]
        for _ in range(self.FAILED_JOBS_RESTART_COUNT):
            while not job.completed:
                self.logger.info(f"Job {job} is not ready, wait for {self.JOB_STATUS_UPDATE_SLEEP_SECONDS} seconds")
                time.sleep(self.JOB_STATUS_UPDATE_SLEEP_SECONDS)
            if job.failed:
                self.logger.info(f"Job {job} failed, restarting")
                job.restart()
                continue
            self.add_async_jobs()
            return self._jobs_queue.popleft()
        else:
            # TODO: Break range into smaller parts if job failing constantly
            raise Exception(f"Job {job} failed")

    def _update_api_throttle_limit(self):
        self.api.account.get_insights()
