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
import logging

import pendulum
from typing import Any, Iterable, Mapping, Optional, MutableMapping, List

from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.async_source import AsyncJob
from cached_property import cached_property

import backoff

from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.common import retry_pattern, deep_merge
from source_facebook_marketing.streams import FBMarketingIncrementalStream
from source_facebook_marketing.async_streams import AsyncStream

from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)


class JobWaitTimeout(Exception):
    """Job took too long to finish"""


class JobFailed(Exception):
    """Job finished with failed status"""


class InsightAsyncJob(AsyncJob):
    job_wait_timeout = None

    def __init__(self, api, params, breakdowns):
        self._api = api
        self._breakdowns = breakdowns
        self._params = params
        self._job = None
        self._result = None

    @abstractmethod
    def start_job(self) -> None:
        """Create async job and return"""
        job = self._api.account.get_insights(params=self._params, is_async=True)
        job_id = job["report_run_id"]
        time_range = self._params["time_range"]
        logger.info(f"Created AdReportRun: {job_id} to sync insights {time_range} with breakdown {self._breakdowns}")
        self._job = job

    @abstractmethod
    def check_status(self) -> bool:
        """Something that will tell if job was successful"""
        job_status = self._job.api_get()
        logger.info(f"ReportRunId {job_status['report_run_id']} is {job_status['async_percent_completion']}% complete")

        if job_status["async_status"] == "Job Completed":
            return True

        if job_status["async_status"] == "Job Failed":
            raise JobFailed(f"AdReportRun {job_status} failed.")

        if job_status["async_status"] == "Job Skipped":
            raise JobFailed(f"AdReportRun {job_status} skipped.")

        return False

    def get_result(self) -> Any:
        """Reading job result, separate function because we want this to happen after we retrieved jobs in particular order"""
        if not self._result:
            super().get_result()
            self._result = self._job.get_result()

        return self._result

    @backoff_policy
    def fetch_job_result(self, job):
        for obj in job.get_result():
            yield obj.export_all_data()


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

    INSIGHTS_RETENTION_PERIOD = pendulum.duration(days=37 * 30)

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    time_increment = 1

    def __init__(self, buffer_days, days_per_job, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window = pendulum.duration(days=buffer_days)
        self._days_per_job = days_per_job

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

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params = deep_merge(
            params,
            {
                "level": "ad",
                "action_breakdowns": self.action_breakdowns,
                "breakdowns": self.breakdowns,
                "fields": self.fields,
                "time_increment": self.time_increment,
                "action_attribution_windows": self.ALL_ACTION_ATTRIBUTION_WINDOWS,
            },
        )

        return params

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
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
            params = self.request_params(stream_state=stream_state, stream_slice={
                "time_range": {"since": since.to_date_string(), "until": until.to_date_string()},
            })
            yield InsightAsyncJob(api=self._api, params=params, breakdowns=self.breakdowns)


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
