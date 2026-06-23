#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import itertools
import re
from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


PINTEREST_STATUS_CHUNK_SIZE = 6


class AdAccountRecordExtractor(RecordExtractor):
    """
    Custom extractor for handling different response formats from the Ad Accounts endpoint.

    This extractor is necessary to handle cases where an `account_id` is present in the request.
    - When querying all ad accounts, the response contains an "items" key with a list of accounts.
    - When querying a specific ad account, the response returns a single dictionary representing that account.
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        data = response.json()

        if not data:
            return []

        # Extract records from "items" if present
        if isinstance(data, dict) and "items" in data:
            return data["items"]

        # If the response is a single object, wrap it in a list
        if isinstance(data, dict):
            return [data]
        return []


class PinterestAnalyticsBackoffStrategy(BackoffStrategy):
    _re = re.compile(r"Retry after\s+(\d+)\s+seconds", re.IGNORECASE)

    def backoff_time(self, response_or_exception, attempt_count: int) -> float:
        try:
            if isinstance(response_or_exception, requests.Response):
                data = response_or_exception.json()
                msg = str(data.get("message", ""))
                m = self._re.search(msg)
                if m:
                    return float(m.group(1))
        except Exception:
            pass
        return min(2**attempt_count, 120.0)


@dataclass
class StatusChunkPartitionRouter(PartitionRouter):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    campaign_statuses: Optional[List[str]] = field(default=None)
    ad_group_statuses: Optional[List[str]] = field(default=None)
    ad_statuses: Optional[List[str]] = field(default=None)

    @staticmethod
    def _chunk(values: Optional[List[str]]) -> List[Optional[List[str]]]:
        if not values:
            return [None]
        return [values[i : i + PINTEREST_STATUS_CHUNK_SIZE] for i in range(0, len(values), PINTEREST_STATUS_CHUNK_SIZE)]

    def stream_slices(self) -> Iterable[StreamSlice]:
        for campaign_chunk, ad_group_chunk, ad_chunk in itertools.product(
            self._chunk(self.campaign_statuses),
            self._chunk(self.ad_group_statuses),
            self._chunk(self.ad_statuses),
        ):
            partition: dict[str, Any] = {}
            if campaign_chunk is not None:
                partition["campaign_statuses_chunk"] = campaign_chunk
            if ad_group_chunk is not None:
                partition["ad_group_statuses_chunk"] = ad_group_chunk
            if ad_chunk is not None:
                partition["ad_statuses_chunk"] = ad_chunk
            yield StreamSlice(partition=partition, cursor_slice={})

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        return {}

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_stream_state(self) -> Optional[Mapping[str, StreamState]]:
        return None
