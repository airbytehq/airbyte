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

import time
import urllib.parse as urlparse
from abc import ABC
from collections import deque
from datetime import datetime
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Sequence, Union

import backoff
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from cached_property import cached_property
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.api import FacebookAdsApiBatch, FacebookRequest, FacebookResponse
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.api import API

from .common import FacebookAPIException, JobTimeoutException, batch, deep_merge, retry_pattern

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)


def remove_params_from_url(url: str, params: List[str]) -> str:
    """
    Parses a URL and removes the query parameters specified in params
    :param url: URL
    :param params: list of query parameters
    :return: URL with params removed
    """
    parsed = urlparse.urlparse(url)
    query = urlparse.parse_qs(parsed.query, keep_blank_values=True)
    filtered = dict((k, v) for k, v in query.items() if k not in params)
    return urlparse.urlunparse(
        [parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlparse.urlencode(filtered, doseq=True), parsed.fragment]
    )


class FBMarketingStream(Stream, ABC):
    """Base stream class"""

    primary_key = "id"

    page_size = 100

    enable_deleted = False
    entity_prefix = None

    def __init__(self, api: API, include_deleted: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._api = api
        self._include_deleted = include_deleted if self.enable_deleted else False

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        return list(self.get_json_schema().get("properties", {}).keys())

    @backoff_policy
    def execute_in_batch(self, requests: Iterable[FacebookRequest]) -> Sequence[MutableMapping[str, Any]]:
        """Execute list of requests in batches"""
        records = []

        def success(response: FacebookResponse):
            records.append(response.json())

        def failure(response: FacebookResponse):
            raise response.error()

        api_batch: FacebookAdsApiBatch = self._api.api.new_batch()
        for request in requests:
            api_batch.add_request(request, success=success, failure=failure)
        retry_batch = api_batch.execute()
        if retry_batch:
            raise FacebookAPIException(f"Batch has failed {len(retry_batch)} requests")

        return records

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Main read method used by CDK"""
        for record in self._read_records(params=self.request_params(stream_state=stream_state)):
            yield self.transform(self._extend_record(record, fields=self.fields))

    def transform(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Use this method to remove update fields types in record according to schema.
        """
        schema = self.get_json_schema()
        self.convert_to_schema_types(record, schema["properties"])
        return record

    def get_python_type(self, _types: Union[list, str]) -> tuple:
        """Converts types from schema to python types. Examples:
        - `["string", "null"]` will be converted to `(str,)`
        - `["array", "string", "null"]` will be converted to `(list, str,)`
        - `"boolean"` will be converted to `(bool,)`
        """
        types_mapping = {
            "string": str,
            "number": float,
            "integer": int,
            "object": dict,
            "array": list,
            "boolean": bool,
        }

        if isinstance(_types, list):
            return tuple([types_mapping[t] for t in _types if t != "null"])

        return (types_mapping[_types],)

    def convert_to_schema_types(self, record: Mapping[str, Any], schema: Mapping[str, Any]):
        """
        Converts values' type from record to appropriate type from schema. For example, let's say we have `reach` value
        and in schema it has `number` type because it's, well, a number, but from API we are getting `reach` as string.
        This function fixes this and converts `reach` value from `string` to `number`. Same for all fields and all
        types from schema.
        """
        if not schema:
            return

        for key, value in record.items():
            if key not in schema:
                continue

            if isinstance(value, dict):
                self.convert_to_schema_types(record=value, schema=schema[key].get("properties", {}))
            elif isinstance(value, list) and "items" in schema[key]:
                for record_list_item in value:
                    if list in self.get_python_type(schema[key]["items"]["type"]):
                        # TODO Currently we don't have support for list of lists.
                        pass
                    elif dict in self.get_python_type(schema[key]["items"]["type"]):
                        self.convert_to_schema_types(record=record_list_item, schema=schema[key]["items"]["properties"])
                    elif not isinstance(record_list_item, self.get_python_type(schema[key]["items"]["type"])):
                        record[key] = self.get_python_type(schema[key]["items"]["type"])[0](record_list_item)
            elif not isinstance(value, self.get_python_type(schema[key]["type"])):
                record[key] = self.get_python_type(schema[key]["type"])[0](value)

    def _read_records(self, params: Mapping[str, Any]) -> Iterable:
        """Wrapper around query to backoff errors.
        We have default implementation because we still can override read_records so this method is not mandatory.
        """
        return []

    @backoff_policy
    def _extend_record(self, obj: Any, **kwargs):
        """Wrapper around api_get to backoff errors"""
        return obj.api_get(**kwargs).export_all_data()

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        """Parameters that should be passed to query_records method"""
        params = {"limit": self.page_size}

        if self._include_deleted:
            params.update(self._filter_all_statuses())

        return params

    def _filter_all_statuses(self) -> MutableMapping[str, Any]:
        """Filter that covers all possible statuses thus including deleted/archived records"""
        filt_values = [
            "active",
            "archived",
            "completed",
            "limited",
            "not_delivering",
            "deleted",
            "not_published",
            "pending_review",
            "permanently_deleted",
            "recently_completed",
            "recently_rejected",
            "rejected",
            "scheduled",
            "inactive",
        ]

        return {
            "filtering": [
                {"field": f"{self.entity_prefix}.delivery_info", "operator": "IN", "value": filt_values},
            ],
        }


class FBMarketingIncrementalStream(FBMarketingStream, ABC):
    cursor_field = "updated_time"

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.instance(start_date)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """Update stream state from latest record"""
        potentially_new_records_in_the_past = self._include_deleted and not current_stream_state.get("include_deleted", False)
        record_value = latest_record[self.cursor_field]
        state_value = current_stream_state.get(self.cursor_field) or record_value
        max_cursor = max(pendulum.parse(state_value), pendulum.parse(record_value))
        if potentially_new_records_in_the_past:
            max_cursor = record_value

        return {
            self.cursor_field: str(max_cursor),
            "include_deleted": self._include_deleted,
        }

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """Include state filter"""
        params = super().request_params(**kwargs)
        params = deep_merge(params, self._state_filter(stream_state=stream_state or {}))
        return params

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Additional filters associated with state if any set"""
        state_value = stream_state.get(self.cursor_field)
        filter_value = self._start_date if not state_value else pendulum.parse(state_value)

        potentially_new_records_in_the_past = self._include_deleted and not stream_state.get("include_deleted", False)
        if potentially_new_records_in_the_past:
            self.logger.info(f"Ignoring bookmark for {self.name} because of enabled `include_deleted` option")
            filter_value = self._start_date

        return {
            "filtering": [
                {
                    "field": f"{self.entity_prefix}.{self.cursor_field}",
                    "operator": "GREATER_THAN",
                    "value": filter_value.int_timestamp,
                },
            ],
        }


class AdCreatives(FBMarketingStream):
    """AdCreative is append only stream
    doc: https://developers.facebook.com/docs/marketing-api/reference/ad-creative
    """

    entity_prefix = "adcreative"
    batch_size = 50

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read records using batch API"""
        records = self._read_records(params=self.request_params(stream_state=stream_state))
        requests = [record.api_get(fields=self.fields, pending=True) for record in records]
        for requests_batch in batch(requests, size=self.batch_size):
            for record in self.execute_in_batch(requests_batch):
                yield self.clear_urls(record)

    @staticmethod
    def clear_urls(record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """Some URLs has random values, these values doesn't affect validity of URLs, but breaks SAT"""
        thumbnail_url = record.get("thumbnail_url")
        if thumbnail_url:
            record["thumbnail_url"] = remove_params_from_url(thumbnail_url, ["_nc_hash", "d"])
        return record

    @backoff_policy
    def _read_records(self, params: Mapping[str, Any]) -> Iterator:
        return self._api.account.get_ad_creatives(params=params)


class Ads(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup"""

    entity_prefix = "ad"
    enable_deleted = True

    @backoff_policy
    def _read_records(self, params: Mapping[str, Any]):
        return self._api.account.get_ads(params=params, fields=[self.cursor_field])


class AdSets(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign"""

    entity_prefix = "adset"
    enable_deleted = True

    @backoff_policy
    def _read_records(self, params: Mapping[str, Any]):
        return self._api.account.get_ad_sets(params=params)


class Campaigns(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group"""

    entity_prefix = "campaign"
    enable_deleted = True

    @backoff_policy
    def _read_records(self, params: Mapping[str, Any]):
        return self._api.account.get_campaigns(params=params)


class AdsInsights(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/insights"""

    cursor_field = "date_start"
    primary_key = None

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
    MAX_ASYNC_JOBS = 10
    INSIGHTS_RETENTION_PERIOD = pendulum.duration(days=37 * 30)

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1

    breakdowns = []

    def __init__(self, buffer_days, days_per_job, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window = pendulum.duration(days=buffer_days)
        self._days_per_job = days_per_job

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Waits for current job to finish (slice) and yield its result"""
        result = self.wait_for_job(stream_slice["job"])
        # because we query `lookback_window` days before actual cursor we might get records older then cursor

        for obj in result.get_result():
            yield self.transform(obj.export_all_data())

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Slice by date periods and schedule async job for each period, run at most MAX_ASYNC_JOBS jobs at the same time.
        This solution for Async was chosen because:
        1. we should commit state after each successful job
        2. we should run as many job as possible before checking for result
        3. we shouldn't proceed to consumption of the next job before previous succeed
        """
        stream_state = stream_state or {}
        running_jobs = deque()
        date_ranges = list(self._date_ranges(stream_state=stream_state))
        for params in date_ranges:
            params = deep_merge(params, self.request_params(stream_state=stream_state))
            job = self._create_insights_job(params)
            running_jobs.append(job)
            if len(running_jobs) >= self.MAX_ASYNC_JOBS:
                yield {"job": running_jobs.popleft()}

        while running_jobs:
            yield {"job": running_jobs.popleft()}

    @backoff_policy
    def wait_for_job(self, job) -> AdReportRun:
        factor = 2
        start_time = pendulum.now()
        sleep_seconds = factor
        while True:
            job = job.api_get()
            job_progress_pct = job["async_percent_completion"]
            job_id = job["report_run_id"]
            self.logger.info(f"ReportRunId {job_id} is {job_progress_pct}% complete ({job['async_status']})")
            runtime = pendulum.now() - start_time

            if job["async_status"] == "Job Completed":
                return job
            elif job["async_status"] == "Job Failed":
                raise JobTimeoutException(f"AdReportRun {job} failed after {runtime.in_seconds()} seconds.")
            elif job["async_status"] == "Job Skipped":
                raise JobTimeoutException(f"AdReportRun {job} skipped after {runtime.in_seconds()} seconds.")

            if runtime > self.MAX_WAIT_TO_START and job_progress_pct == 0:
                raise JobTimeoutException(
                    f"AdReportRun {job} did not start after {runtime.in_seconds()} seconds."
                    f" This is an intermittent error which may be fixed by retrying the job. Aborting."
                )
            elif runtime > self.MAX_WAIT_TO_FINISH:
                raise JobTimeoutException(
                    f"AdReportRun {job} did not finish after {runtime.in_seconds()} seconds."
                    f" This is an intermittent error which may be fixed by retrying the job. Aborting."
                )
            self.logger.info(f"Sleeping {sleep_seconds} seconds while waiting for AdReportRun: {job_id} to complete")
            time.sleep(sleep_seconds)
            if sleep_seconds < self.MAX_ASYNC_SLEEP.in_seconds():
                sleep_seconds *= factor

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

    def _date_ranges(self, stream_state: Mapping[str, Any]) -> Iterator[dict]:
        """Iterate over period between start_date/state and now

        Notes: Facebook freezes insight data 28 days after it was generated, which means that all data
            from the past 28 days may have changed since we last emitted it, so we retrieve it again.
        """
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

    @backoff_policy
    def _create_insights_job(self, params) -> AdReportRun:
        job = self._api.account.get_insights(params=params, is_async=True)
        job_id = job["report_run_id"]
        time_range = params["time_range"]
        self.logger.info(f"Created AdReportRun: {job_id} to sync insights {time_range} with breakdown {self.breakdowns}")
        return job


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


class AdsInsightsActionType(AdsInsights):
    breakdowns = []
    action_breakdowns = ["action_type"]
