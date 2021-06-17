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
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Sequence

import backoff
import pendulum as pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.api import FacebookAdsApiBatch, FacebookRequest, FacebookResponse
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.api import API

from .common import FacebookAPIException, JobTimeoutException, batch, deep_merge, retry_pattern

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)


class FBMarketingStream(Stream, ABC):
    primary_key = "id"

    page_size = 100

    enable_deleted = False
    entity_prefix = None

    def __init__(self, api: API, include_deleted: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._api = api
        self._include_deleted = include_deleted if self.enable_deleted else False

    @property
    def fields(self) -> List[str]:
        return list(self.get_json_schema().get("properties", {}).keys())

    @backoff_policy
    def execute_in_batch(self, requests: Iterable[FacebookRequest]) -> Sequence[MutableMapping[str, Any]]:
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
        for record in self.request_records(params=self.request_params(stream_state=stream_state)):
            yield from self._extend_record(record, fields=self.fields)

    @abstractmethod
    def request_records(self, params: Mapping[str, Any]):
        """Implement this method to return stream entities"""

    @backoff_policy
    def _extend_record(self, obj: Any, **kwargs):
        """Request additional attributes for object"""
        return obj.api_get(**kwargs).export_all_data()

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = {
            "limit": self.page_size
        }

        if self._include_deleted:
            params.update(self._filter_all_statuses())

        return params

    def _filter_all_statuses(self) -> MutableMapping[str, Any]:
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
        record_value = latest_record[self.cursor_field]
        state_value = current_stream_state.get(self.cursor_field) or record_value
        max_cursor = max(pendulum.parse(state_value), pendulum.parse(record_value))

        return {
            self.cursor_field: str(max_cursor),
            "include_deleted": self._include_deleted,
        }

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        deep_merge(params, self._state_filter(stream_state=stream_state))
        return params

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Additional filters associated with state if any set"""
        state_value = stream_state.get(self.cursor_field)
        filter_value = pendulum.parse(state_value) if stream_state else self._start_date

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
        """ Read records using batch API
        """
        creatives = self._get_creatives(params=self.request_params(stream_state=stream_state))
        requests = [self._extend_record(creative, fields=self.fields, pending=True) for creative in creatives]
        for requests_batch in batch(requests, size=self.batch_size):
            yield from self.execute_in_batch(requests_batch)

    @backoff_policy
    def _get_creatives(self, params: Mapping[str, Any]) -> Iterator:
        return self._api.account.get_ad_creatives(params=params)


class Ads(FBMarketingIncrementalStream):
    """ doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup """

    entity_prefix = "ad"
    enable_deleted = True

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in self._get_ads(params=self.request_params(stream_state=stream_state)):
            yield from self._extend_record(record, fields=self.fields)

    @backoff_policy
    def _get_ads(self, params: Mapping[str, Any]) -> Iterator:
        return self._api.account.get_ads(params=params)


class AdSets(FBMarketingIncrementalStream):
    """ doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign """

    entity_prefix = "adset"
    enable_deleted = True

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in self._get_ad_sets(params=self.request_params(stream_state=stream_state)):
            yield from self._extend_record(record, fields=self.fields)

    @backoff_policy
    def _get_ad_sets(self, params):
        return self._api.account.get_ad_sets(params=params)


class Campaigns(FBMarketingIncrementalStream):
    """ doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group """

    entity_prefix = "campaign"
    enable_deleted = True

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in self._get_campaigns(params=self.request_params(stream_state=stream_state)):
            yield from self._extend_record(record, fields=self.fields)

    @backoff_policy
    def _get_campaigns(self, params):
        return self._api.account.get_campaigns(params=params)


class AdsInsights(FBMarketingIncrementalStream):
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

    # Some automatic fields (primary-keys) cannot be used as 'fields' query params.
    INVALID_INSIGHT_FIELDS = [
        "impression_device",
        "publisher_platform",
        "platform_position",
        "age",
        "gender",
        "country",
        "placement",
        "region",
        "dma",
    ]

    MAX_WAIT_TO_START = pendulum.Interval(minutes=5)
    MAX_WAIT_TO_FINISH = pendulum.Interval(minutes=30)
    MAX_ASYNC_SLEEP = pendulum.Interval(minutes=5)

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1

    breakdowns = None

    def __init__(self, buffer_days, days_per_job, **kwargs):
        super().__init__(**kwargs)
        self._buffer_days = buffer_days
        self._sync_interval = pendulum.Interval(days=days_per_job)
        self._state = self._start_date

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        jobs = []
        for params in self._date_params():
            deep_merge(params, self.request_params(stream_state=stream_state))
            jobs.append(self._get_insights(params))

        for job in jobs:
            result = self.wait_for_job(job)
            for obj in result.get_result():
                yield obj.export_all_data()

    @backoff_policy
    def wait_for_job(self, job) -> AdReportRun:
        factor = 2
        start_time = pendulum.now()
        sleep_seconds = factor
        while True:
            job = job.api_get()
            job_progress_pct = job["async_percent_completion"]
            self.logger.info(f"ReportRunId {job['report_run_id']} is {job_progress_pct}% complete")
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
            self.logger.info(f"Sleeping {sleep_seconds} seconds while waiting for AdReportRun: {job} to complete")
            time.sleep(sleep_seconds)
            if sleep_seconds < self.MAX_ASYNC_SLEEP.in_seconds():
                sleep_seconds *= factor

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        deep_merge(params, {
            "level": self.level,
            "action_breakdowns": self.action_breakdowns,
            "breakdowns": self.breakdowns,
            "fields": self.fields,
            "time_increment": self.time_increment,
            "action_attribution_windows": self.action_attribution_windows,
        })

        return params

    @property
    def fields(self) -> List[str]:
        return list(set(super().fields) - set(self.INVALID_INSIGHT_FIELDS))

    def _date_params(self) -> Iterator[dict]:
        # Facebook freezes insight data 28 days after it was generated, which means that all data
        # from the past 28 days may have changed since we last emitted it, so we retrieve it again.
        buffered_start_date = self._state - pendulum.Interval(days=self._buffer_days)
        end_date = pendulum.now()
        while buffered_start_date <= end_date:
            buffered_end_date = buffered_start_date + self._sync_interval
            yield {
                "time_range": {"since": buffered_start_date.to_date_string(), "until": buffered_end_date.to_date_string()},
            }

            buffered_start_date = buffered_end_date

    @backoff_policy
    def _get_insights(self, params) -> AdReportRun:
        job = self._api.account.get_insights(params=params, is_async=True)
        self.logger.info(f"Created AdReportRun: {job} to sync insights with breakdown {self.breakdowns}")
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
