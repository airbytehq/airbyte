#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import backoff
import pendulum
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.api import API

from .common import JobTimeoutException, retry_pattern, JobException
import logging

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
logger = logging.getLogger(__name__)

class AsyncJob:
    MAX_WAIT_TO_START = pendulum.duration(minutes=5)
    MAX_WAIT_TO_FINISH = pendulum.duration(minutes=30)

    def __init__(self, api: API, params: Mapping[str, Any]):
        """ Initialize

        :param api:
        :param params:
        """
        self._params = params
        self._api = api
        self._job = None
        self._start_time = None
        self._finish_time = None
        self._failed = False

    @backoff_policy
    def start(self):
        """ Start remote job"""
        if self._job:
            raise RuntimeError("Incorrect usage of method - the job already started, use restart instead")

        self._job = self._api.account.get_insights(params=self._params, is_async=True)
        self._start_time = pendulum.now()
        job_id = self._job["report_run_id"]
        time_range = self._params["time_range"]
        breakdowns = self._params["breakdowns"]
        logger.info(f"Created AdReportRun: {job_id} to sync insights {time_range} with breakdown {breakdowns}")

    def restart(self):
        if not self._job and not self.failed:
            raise RuntimeError("Incorrect usage of method - only failed jobs can be restarted")

        self._failed = False
        self._finish_time = None
        self.start()

    @property
    def elapsed_time(self):
        if not self._start_time:
            return None

        end_time = self._finish_time or pendulum.now()
        return end_time - self._start_time

    @property
    def completed(self):
        try:
            return self._check_status()
        except JobException:
            self._failed = True
            raise

    @property
    def failed(self):
        return self._failed

    @backoff_policy
    def _check_status(self):
        job = self._job.api_get()
        job_progress_pct = job["async_percent_completion"]
        logger.info(f"{self} is {job_progress_pct}% complete ({job['async_status']})")
        runtime = self.elapsed_time

        if job["async_status"] == "Job Completed":
            self._finish_time = pendulum.now()
            return True
        elif job["async_status"] == "Job Failed":
            raise JobException(f"AdReportRun {job} failed after {runtime.in_seconds()} seconds.")
        elif job["async_status"] == "Job Skipped":
            raise JobException(f"AdReportRun {job} skipped after {runtime.in_seconds()} seconds.")
        self._job = job

        if runtime > self.MAX_WAIT_TO_START and self._job["async_percent_completion"] == 0:
            raise JobTimeoutException(
                f"AdReportRun {job} did not start after {runtime.in_seconds()} seconds."
                f" This is an intermittent error which may be fixed by retrying the job. Aborting."
            )
        elif runtime > self.MAX_WAIT_TO_FINISH:
            raise JobTimeoutException(
                f"AdReportRun {job} did not finish after {runtime.in_seconds()} seconds."
                f" This is an intermittent error which may be fixed by retrying the job. Aborting."
            )
        return False

    @backoff_policy
    def get_result(self):
        return self._job.get_result()

    def __str__(self):
        job_id = self._job["report_run_id"] if self._job else '<None>'
        time_range = self._params["time_range"]
        breakdowns = self._params["breakdowns"]
        return f"AdReportRun(id={job_id}, time_range={time_range}, breakdowns={breakdowns}"
