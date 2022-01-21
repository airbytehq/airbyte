#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import base64
import logging
import urllib.parse as urlparse
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Sequence, TYPE_CHECKING

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from cached_property import cached_property
from facebook_business.api import FacebookAdsApiBatch, FacebookRequest, FacebookResponse
from .common import batch, deep_merge

if TYPE_CHECKING:
    from source_facebook_marketing.api import API

logger = logging.getLogger("airbyte")


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

    def __init__(self, api: 'API', include_deleted: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._api = api
        self._include_deleted = include_deleted if self.enable_deleted else False

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        return list(self.get_json_schema().get("properties", {}).keys())

    def execute_in_batch(self, requests: Iterable[FacebookRequest]) -> Sequence[MutableMapping[str, Any]]:
        """Execute list of requests in batches"""
        records = []

        def success(response: FacebookResponse):
            records.append(response.json())

        def failure(response: FacebookResponse):
            logger.info(f"Request failed with response: {response.body()}")

        api_batch: FacebookAdsApiBatch = self._api.api.new_batch()
        for request in requests:
            api_batch.add_request(request, success=success, failure=failure)

        while api_batch:
            api_batch = api_batch.execute()
            if api_batch:
                logger.info("Retry failed requests in batch")

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

    def _read_records(self, params: Mapping[str, Any]) -> Iterator:
        return self._api.account.get_ad_creatives(params=params)


class Ads(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup"""

    entity_prefix = "ad"
    enable_deleted = True

    def _read_records(self, params: Mapping[str, Any]):
        return self._api.account.get_ads(params=params, fields=[self.cursor_field])


class AdSets(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign"""

    entity_prefix = "adset"
    enable_deleted = True

    def _read_records(self, params: Mapping[str, Any]):
        return self._api.account.get_ad_sets(params=params)


class Campaigns(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group"""

    entity_prefix = "campaign"
    enable_deleted = True

    def _read_records(self, params: Mapping[str, Any]):
        return self._api.account.get_campaigns(params=params)


class Videos(FBMarketingIncrementalStream):
    """See: https://developers.facebook.com/docs/marketing-api/reference/video"""

    entity_prefix = "video"
    enable_deleted = True

    def _read_records(self, params: Mapping[str, Any]) -> Iterator:
        return self._api.account.get_ad_videos(params=params)
