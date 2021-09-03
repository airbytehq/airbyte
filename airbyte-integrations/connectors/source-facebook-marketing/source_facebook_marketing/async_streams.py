#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import asyncio

import pendulum
from pendulum import duration
from typing import Any, Iterable, Mapping, Optional, MutableMapping, List

from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from cached_property import cached_property

import backoff

from abc import ABC, abstractmethod
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.common import retry_pattern, deep_merge
from source_facebook_marketing.streams import FBMarketingIncrementalStream

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)


class JobWaitTimeout(Exception):
    """Job took too long to finish"""


class JobFailed(Exception):
    """Job finished with failed status"""


class AsyncStream(Stream, ABC):
    job_wait_timeout = None

    @abstractmethod
    @property
    def job_limit(self):
        """"""

    @property
    def job_sleep_intervals(self) -> Iterable[duration]:
        """Sleep interval, also represents max number of retries"""
        return [duration(seconds=secs) for secs in list(range(5)) * 2]

    def print(self, *args):
        print(self.name, *args)

    @backoff_policy
    async def create_and_wait(self, stream_slice):
        """Single wait routing because we would like to re-create job in case its result is fail"""
        job = await self.create_job(stream_slice)
        await self.wait_for_job(job)

    @abstractmethod
    async def check_job_status(self, job) -> bool:
        """Something that will tell if job was successful"""

    @backoff_policy
    async def wait_for_job(self, job):
        """Actual waiting for job to finish"""
        self.print("waiting job", job)
        start_time = pendulum.now()
        for sleep_interval in self.job_sleep_intervals:
            finished_and_ok = await self.check_job_status(job)
            if finished_and_ok:
                break
            self.print(f"Sleeping {sleep_interval.total_seconds()} seconds while waiting for Job: {job} to complete")
            await asyncio.sleep(sleep_interval.total_seconds())
            # do we really need this?
            if self.job_wait_timeout and pendulum.now() - start_time > self.job_wait_timeout:
                raise JobWaitTimeout("Waiting for job more than allowed")
        else:
            # or this will be enough
            raise JobWaitTimeout("Waiting for job more than allowed")
        self.print("job finished")

    @abstractmethod
    async def fetch_job_result(self, job):
        """Reading job result, separate function because we want this to happen after we retrieved jobs in particular order"""

    @abstractmethod
    async def stream_slices(self, **kwargs):
        """Required to be async by aiostream lib in order to use stream.map"""
        yield None


class AdsInsights(AsyncStream, FBMarketingIncrementalStream):
    cursor_field = "date_start"
    primary_key = None

    job_limit = 10
    breakdowns = []

    ALL_ACTION_ATTRIBUTION_WINDOWS = [
        "1d_click",
        "7d_click",
        "28d_click",
        "1d_view",
        "7d_view",
        "28d_view",
    ]

    ALL_ACTION_BREAKDOWNS = [
        "action_type",
        "action_target_id",
        "action_destination",
    ]

    MAX_WAIT_TO_START = pendulum.duration(minutes=5)
    MAX_WAIT_TO_FINISH = pendulum.duration(minutes=30)
    MAX_ASYNC_SLEEP = pendulum.duration(minutes=5)
    INSIGHTS_RETENTION_PERIOD = pendulum.duration(days=37 * 30)

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1

    def __init__(self, buffer_days, days_per_job, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window = pendulum.duration(days=buffer_days)
        self._days_per_job = days_per_job

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params = deep_merge(
            params,
            {
                "level": self.level,
                "action_breakdowns": self.action_breakdowns,
                "breakdowns": self.breakdowns,
                "fields": self.fields,
                "time_increment": self.time_increment,
                "action_attribution_windows": self.action_attribution_windows,
            },
        )

        return params

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Works differently for insights, so remove it"""
        return {}

    def get_json_schema(self) -> Mapping[str, Any]:
        """Add fields from breakdowns to the stream schema
        :return: A dict of the JSON schema representing this stream.
        """
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights")
        schema["properties"].update(self._schema_for_breakdowns())
        return schema

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights")
        return list(schema.get("properties", {}).keys())

    def _schema_for_breakdowns(self) -> Mapping[str, Any]:
        """Breakdown fields and their type"""
        schemas = {
            "age": {"type": ["null", "integer", "string"]},
            "gender": {"type": ["null", "string"]},
            "country": {"type": ["null", "string"]},
            "dma": {"type": ["null", "string"]},
            "region": {"type": ["null", "string"]},
            "impression_device": {"type": ["null", "string"]},
            "placement": {"type": ["null", "string"]},
            "platform_position": {"type": ["null", "string"]},
            "publisher_platform": {"type": ["null", "string"]},
        }
        breakdowns = self.breakdowns[:]
        if "platform_position" in breakdowns:
            breakdowns.append("placement")

        return {breakdown: schemas[breakdown] for breakdown in self.breakdowns}

    @backoff_policy
    async def create_job(self, stream_slice, params) -> Any:
        job = self._api.account.get_insights(params=params, is_async=True)
        job_id = job["report_run_id"]
        time_range = params["time_range"]
        self.logger.info(f"Created AdReportRun: {job_id} to sync insights {time_range} with breakdown {self.breakdowns}")
        return job

    @backoff_policy
    async def check_job_status(self, job) -> bool:
        """Tell us if job is ready"""
        job_status = job.api_get()
        self.logger.info(f"ReportRunId {job_status['report_run_id']} is {job_status['async_percent_completion']}% complete")

        if job_status["async_status"] == "Job Completed":
            return job
        elif job_status["async_status"] == "Job Failed":
            raise JobFailed(f"AdReportRun {job_status} failed.")
        elif job_status["async_status"] == "Job Skipped":
            raise JobFailed(f"AdReportRun {job_status} skipped.")

    @backoff_policy
    async def fetch_job_result(self, job):
        for obj in job.get_result():
            yield obj.export_all_data()

    async def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Slice by date periods"""
        state_value = stream_state.get(self.cursor_field)
        if state_value:
            start_date = pendulum.parse(state_value) - self.lookback_window
        else:
            start_date = self._start_date
        end_date = pendulum.now()
        start_date = max(end_date - self.INSIGHTS_RETENTION_PERIOD, start_date)

        for since in pendulum.period(start_date, end_date).range("days", self._days_per_job):
            until = min(since.add(days=self._days_per_job - 1), end_date)  # -1 because time_range is inclusive
            yield {
                "time_range": {"since": since.to_date_string(), "until": until.to_date_string()},
            }


class AdsInsightsAgeAndGender(AdsInsights):
    breakdowns = ["age", "gender"]


class AdsInsightsCountry(AdsInsights):
    breakdowns = ["country"]


class AdsInsightsRegion(AdsInsights):
    breakdowns = ["region"]


class AdsInsightsDma(AdsInsights):
    breakdowns = ["dma"]


class AdsInsightsPlatformAndDevice(AdsInsights):
    breakdowns = ["publisher_platform", "platform_position", "impression_device"]
    action_breakdowns = ["action_type"]  # FB Async Job fails for unknown reason if we set other breakdowns
