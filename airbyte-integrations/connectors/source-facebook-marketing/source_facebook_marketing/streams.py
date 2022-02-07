#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import base64
import time
import urllib.parse as urlparse
from abc import ABC
from collections import deque
from datetime import datetime
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Sequence

import airbyte_cdk.sources.utils.casing as casing
import backoff
import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from cached_property import cached_property
from facebook_business.api import FacebookAdsApiBatch, FacebookRequest, FacebookResponse
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.api import API

from .async_job import AsyncJob
from .common import FacebookAPIException, JobException, batch, deep_merge, retry_pattern

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


def fetch_thumbnail_data_url(url: str) -> str:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            type = response.headers["content-type"]
            data = base64.b64encode(response.content)
            return f"data:{type};base64,{data.decode('ascii')}"
    except requests.exceptions.RequestException:
        pass
    return None


class FBMarketingStream(Stream, ABC):
    """Base stream class"""

    primary_key = "id"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

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
            yield self._extend_record(record, fields=self.fields)

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

    def __init__(self, start_date: datetime, end_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.instance(start_date)
        self._end_date = pendulum.instance(end_date)

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

    def __init__(self, fetch_thumbnail_images: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._fetch_thumbnail_images = fetch_thumbnail_images

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read records using batch API"""
        records = self._read_records(params=self.request_params(stream_state=stream_state))
        # "thumbnail_data_url" is a field in our stream's schema because we
        # output it (see fix_thumbnail_urls below), but it's not a field that
        # we can request from Facebook
        request_fields = [f for f in self.fields if f != "thumbnail_data_url"]
        requests = [record.api_get(fields=request_fields, pending=True) for record in records]
        for requests_batch in batch(requests, size=self.batch_size):
            for record in self.execute_in_batch(requests_batch):
                yield self.fix_thumbnail_urls(record)

    def fix_thumbnail_urls(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """Cleans and, if enabled, fetches thumbnail URLs for each creative."""
        # The thumbnail_url contains some extra query parameters that don't affect the validity of the URL, but break SAT
        thumbnail_url = record.get("thumbnail_url")
        if thumbnail_url:
            record["thumbnail_url"] = remove_params_from_url(thumbnail_url, ["_nc_hash", "d"])
            if self._fetch_thumbnail_images:
                record["thumbnail_data_url"] = fetch_thumbnail_data_url(thumbnail_url)
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


class Videos(FBMarketingIncrementalStream):
    """See: https://developers.facebook.com/docs/marketing-api/reference/video"""

    entity_prefix = "video"
    enable_deleted = True

    @backoff_policy
    def _read_records(self, params: Mapping[str, Any]) -> Iterator:
        return self._api.account.get_ad_videos(params=params)


class AdsInsights(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/insights"""

    cursor_field = "date_start"
    primary_key = ["account_id", "campaign_id", "adset_id", "ad_id"]

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

    MAX_ASYNC_SLEEP = pendulum.duration(minutes=5)
    MAX_ASYNC_JOBS = 10
    INSIGHTS_RETENTION_PERIOD = pendulum.duration(days=37 * 30)

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1

    breakdowns = []

    def __init__(
        self,
        buffer_days,
        days_per_job,
        name: str = None,
        fields: List[str] = None,
        breakdowns: List[str] = None,
        action_breakdowns: List[str] = None,
        **kwargs,
    ):

        super().__init__(**kwargs)
        self.lookback_window = pendulum.duration(days=buffer_days)
        self._days_per_job = days_per_job
        self._fields = fields
        self.action_breakdowns = action_breakdowns or self.action_breakdowns
        self.breakdowns = breakdowns or self.breakdowns
        self._new_class_name = name

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        name = self._new_class_name or self.__class__.__name__
        return casing.camel_to_snake(name)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Waits for current job to finish (slice) and yield its result"""
        job = self.wait_for_job(stream_slice["job"])
        # because we query `lookback_window` days before actual cursor we might get records older then cursor

        for obj in job.get_result():
            yield obj.export_all_data()

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
            job = AsyncJob(api=self._api, params=params)
            job.start()
            running_jobs.append(job)
            if len(running_jobs) >= self.MAX_ASYNC_JOBS:
                yield {"job": running_jobs.popleft()}

        while running_jobs:
            yield {"job": running_jobs.popleft()}

    @retry_pattern(backoff.expo, JobException, max_tries=10, factor=5)
    def wait_for_job(self, job: AsyncJob) -> AsyncJob:
        if job.failed:
            job.restart()

        factor = 2
        sleep_seconds = factor
        while not job.completed:
            self.logger.info(f"{job}: sleeping {sleep_seconds} seconds while waiting for completion")
            time.sleep(sleep_seconds)
            if sleep_seconds < self.MAX_ASYNC_SLEEP.in_seconds():
                sleep_seconds *= factor

        return job

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
        loader = ResourceSchemaLoader(package_name_from_class(self.__class__))
        schema = loader.get_schema("ads_insights")
        if self._fields:
            schema["properties"] = {k: v for k, v in schema["properties"].items() if k in self._fields}
        if self.breakdowns:
            breakdowns_properties = loader.get_schema("ads_insights_breakdowns")["properties"]
            schema["properties"].update({prop: breakdowns_properties[prop] for prop in self.breakdowns})
        return schema

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        if self._fields:
            return self._fields
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights")
        return list(schema.get("properties", {}).keys())

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
        end_date = self._end_date
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


class AdsInsightsActionType(AdsInsights):
    breakdowns = []
    action_breakdowns = ["action_type"]
