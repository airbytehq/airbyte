#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import itertools
import re
from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


PINTEREST_STATUS_CHUNK_SIZE = 6
STATUS_CHUNK_PARTITION_KEYS = (
    "campaign_statuses_chunk",
    "ad_group_statuses_chunk",
    "ad_statuses_chunk",
)
# Splitting a status filter into multiple requests is only correct when every report row
# belongs to exactly one entity of the filtered dimension - otherwise the same aggregated
# row comes back from several chunks with partial metric sums. A filter may therefore only
# be chunked when the report level is at or below the filtered dimension.
CHUNKABLE_LEVELS_PER_STATUS_FIELD = {
    "campaign_statuses": (
        "CAMPAIGN",
        "CAMPAIGN_TARGETING",
        "AD_GROUP",
        "AD_GROUP_TARGETING",
        "PIN_PROMOTION",
        "PIN_PROMOTION_TARGETING",
        "KEYWORD",
        "PRODUCT_GROUP",
        "PRODUCT_GROUP_TARGETING",
    ),
    "ad_group_statuses": (
        "AD_GROUP",
        "AD_GROUP_TARGETING",
        "PIN_PROMOTION",
        "PIN_PROMOTION_TARGETING",
        "KEYWORD",
        "PRODUCT_GROUP",
        "PRODUCT_GROUP_TARGETING",
    ),
    "ad_statuses": (
        "PIN_PROMOTION",
        "PIN_PROMOTION_TARGETING",
    ),
}


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
    """Chunk custom report status filters into groups of <=6 for Pinterest API compliance.

    Pinterest's async report API limits each status filter field to at most 6 values per
    request. This router splits larger selections into chunks and yields one StreamSlice per
    cartesian combination of chunks; the CDK's CartesianProductStreamSlicer composes these
    with the ad-account SubstreamPartitionRouter so each ad-account x status-chunk pair is
    fetched independently. `level` is the report level from the same custom report config;
    it gates which filters may be chunked (see CHUNKABLE_LEVELS_PER_STATUS_FIELD).
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    campaign_statuses: Optional[List[str]] = field(default=None)
    ad_group_statuses: Optional[List[str]] = field(default=None)
    ad_statuses: Optional[List[str]] = field(default=None)
    level: Optional[str] = field(default=None)

    @staticmethod
    def _chunk(values: Optional[List[str]]) -> List[Optional[List[str]]]:
        # Sorted so the same status SET always yields the same chunks (and therefore the
        # same partition keys) regardless of config array order - reordering values in the
        # UI must not orphan per-partition cursors. Returns [None] for an unconfigured
        # field so the cartesian product still yields exactly one iteration for it.
        if not values:
            return [None]
        values = sorted(values)
        return [values[i : i + PINTEREST_STATUS_CHUNK_SIZE] for i in range(0, len(values), PINTEREST_STATUS_CHUNK_SIZE)]

    def _validate_chunkable_levels(self) -> None:
        if not self.level:
            return
        for field_name, values in (
            ("campaign_statuses", self.campaign_statuses),
            ("ad_group_statuses", self.ad_group_statuses),
            ("ad_statuses", self.ad_statuses),
        ):
            if values and len(values) > PINTEREST_STATUS_CHUNK_SIZE and self.level not in CHUNKABLE_LEVELS_PER_STATUS_FIELD[field_name]:
                message = (
                    f"Custom report: {len(values)} {field_name} values require splitting into multiple API requests, "
                    f"but at report level {self.level} the same aggregated rows would be returned by several requests "
                    f"with partial metric sums. Select at most {PINTEREST_STATUS_CHUNK_SIZE} {field_name} values, or use "
                    f"a report level at or below the filtered dimension "
                    f"({', '.join(CHUNKABLE_LEVELS_PER_STATUS_FIELD[field_name])})."
                )
                raise AirbyteTracedException(message=message, internal_message=message, failure_type=FailureType.config_error)

    def stream_slices(self) -> Iterable[StreamSlice]:
        self._validate_chunkable_levels()
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


class CustomReportStatusChunkStateMigration(StateMigration):
    """Copy pre-chunking per-account cursors onto the new status-chunk partitions.

    Incremental custom reports persist state per partition. Before this change the
    partition was ``{"id": <ad_account_id>}``. With status filters configured it
    becomes ``{"id": ..., "campaign_statuses_chunk": [...], ...}``. Without a
    migration, prior-version state is ignored and the stream re-reads from the
    start date.
    """

    # These bare annotations are load-bearing: create_custom_component filters injected
    # kwargs to get_type_hints(cls), so removing them would stop config/status values
    # from reaching __init__. Do not "clean them up".
    config: Config
    campaign_statuses: Optional[List[str]]
    ad_group_statuses: Optional[List[str]]
    ad_statuses: Optional[List[str]]

    def __init__(
        self,
        config: Config,
        campaign_statuses: Optional[List[str]] = None,
        ad_group_statuses: Optional[List[str]] = None,
        ad_statuses: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self._config = config
        self._campaign_statuses = campaign_statuses
        self._ad_group_statuses = ad_group_statuses
        self._ad_statuses = ad_statuses

    def _legacy_partition_entries(self, stream_state: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        entries = stream_state.get("states")
        if not isinstance(entries, list):
            return []
        legacy_entries = []
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            partition = entry.get("partition")
            if not isinstance(partition, Mapping) or "cursor" not in entry:
                continue
            if "id" in partition and not any(key in partition for key in STATUS_CHUNK_PARTITION_KEYS):
                legacy_entries.append(entry)
        return legacy_entries

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if not stream_state:
            return False
        if not (self._campaign_statuses or self._ad_group_statuses or self._ad_statuses):
            return False
        return bool(self._legacy_partition_entries(stream_state))

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        chunk_partitions = [
            stream_slice.partition
            for stream_slice in StatusChunkPartitionRouter(
                config=self._config,
                parameters={},
                campaign_statuses=self._campaign_statuses,
                ad_group_statuses=self._ad_group_statuses,
                ad_statuses=self._ad_statuses,
            ).stream_slices()
        ]
        legacy_entries = self._legacy_partition_entries(stream_state)
        migrated_states: List[Mapping[str, Any]] = []
        for entry in stream_state.get("states", []):
            if entry not in legacy_entries:
                migrated_states.append(entry)
                continue
            for chunk_partition in chunk_partitions:
                migrated_states.append(
                    {
                        "partition": {**entry["partition"], **chunk_partition},
                        "cursor": entry["cursor"],
                    }
                )
        migrated_state = dict(stream_state)
        migrated_state["states"] = migrated_states
        return migrated_state
