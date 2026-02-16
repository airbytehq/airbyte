"""Tulip Table stream implementation.

Each TulipTableStream represents one Tulip table. Schemas are
discovered dynamically from the Tulip API metadata endpoint.
Supports two-phase incremental sync: BOOTSTRAP then INCREMENTAL.
"""

import json
import logging
from datetime import timedelta
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http.requests_native_auth import BasicHttpAuthenticator
from airbyte_cdk.sources.streams.call_rate import (
    HttpAPIBudget,
    MovingWindowCallRatePolicy,
    Rate,
    HttpRequestMatcher,
)
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy

from source_tulip.utils import (
    SYSTEM_FIELD_NAMES,
    SYSTEM_FIELDS_SCHEMA,
    adjust_cursor_for_overlap,
    build_allowed_fields,
    build_field_mapping,
    generate_column_name,
    map_tulip_type_to_json_schema,
    transform_record,
)

logger = logging.getLogger("airbyte")

DEFAULT_LIMIT = 100
# Tulip API rate limit is 50 req/s. Use 45 to leave headroom.
TULIP_RATE_LIMIT_PER_SECOND = 45


def create_api_budget() -> HttpAPIBudget:
    """Create a shared API budget that enforces Tulip's rate limit.

    Must be shared across all streams so the global 50 req/s limit
    is respected when syncing multiple tables concurrently.
    """
    return HttpAPIBudget(
        policies=[
            MovingWindowCallRatePolicy(
                rates=[
                    Rate(
                        limit=TULIP_RATE_LIMIT_PER_SECOND, interval=timedelta(seconds=1)
                    )
                ],
                matchers=[HttpRequestMatcher()],
            ),
        ],
    )


class TulipBackoffStrategy(BackoffStrategy):
    """Backoff strategy that reads Retry-After header from Tulip 429 responses."""

    def backoff_time(
        self,
        response_or_exception: Optional[
            Union[requests.Response, requests.RequestException]
        ],
        attempt_count: int,
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code == 429:
                retry_after = response_or_exception.headers.get("Retry-After")
                if retry_after:
                    try:
                        return float(retry_after)
                    except (ValueError, TypeError):
                        pass
                return 1.0
        return None


class TulipTableStream(HttpStream, IncrementalMixin):
    """Stream for a single Tulip table.

    Reads records from the Tulip API with cursor-based pagination
    using _sequenceNumber. Supports full refresh and incremental
    sync with a two-phase (BOOTSTRAP -> INCREMENTAL) strategy.
    """

    primary_key = "id"
    cursor_field = "_sequenceNumber"
    state_checkpoint_interval = 500

    def __init__(
        self,
        table_id: str,
        table_label: str,
        table_metadata: Dict[str, Any],
        config: Mapping[str, Any],
        api_budget: Optional[HttpAPIBudget] = None,
        **kwargs: Any,
    ):
        self.table_id = table_id
        self.table_label = table_label
        self._table_metadata = table_metadata
        self.subdomain = config["subdomain"]
        self.api_key = config["api_key"]
        self.api_secret = config["api_secret"]
        self.workspace_id = config.get("workspace_id")
        self.sync_from_date = config.get("sync_from_date")
        self.custom_filters: List[Dict[str, Any]] = json.loads(
            config.get("custom_filter_json", "[]") or "[]"
        )

        self._cursor_value: int = 0
        self._last_updated_at: Optional[str] = None
        self._max_seen_updated_at: Optional[str] = None
        self._cursor_mode: str = "BOOTSTRAP"

        self._field_mapping: Optional[Dict[str, str]] = None
        self._allowed_fields: Optional[List[str]] = None

        authenticator = BasicHttpAuthenticator(
            username=self.api_key,
            password=self.api_secret,
        )
        super().__init__(authenticator=authenticator, api_budget=api_budget, **kwargs)

    def get_backoff_strategy(self) -> Optional[BackoffStrategy]:
        return TulipBackoffStrategy()

    @property
    def name(self) -> str:
        return generate_column_name(self.table_id, self.table_label)

    @property
    def url_base(self) -> str:
        return f"https://{self.subdomain}.tulip.co/api/v3/"

    def path(self, **kwargs: Any) -> str:
        if self.workspace_id:
            return f"w/{self.workspace_id}/tables/{self.table_id}/records"
        return f"tables/{self.table_id}/records"

    # --- State management ---

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {
            "cursor_mode": self._cursor_mode,
            "last_sequence": self._cursor_value,
            "last_updated_at": self._last_updated_at,
        }

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        if not value:
            self._cursor_mode = "BOOTSTRAP"
            self._cursor_value = 0
            self._last_updated_at = self.sync_from_date
            return

        if "cursor_mode" in value:
            self._cursor_mode = value["cursor_mode"]
            self._cursor_value = value.get("last_sequence", 0) or 0
            self._last_updated_at = value.get("last_updated_at", self.sync_from_date)
        elif value.get("last_updated_at"):
            # Migrate old state format -> INCREMENTAL
            self._cursor_mode = "INCREMENTAL"
            self._cursor_value = 0
            self._last_updated_at = value["last_updated_at"]
        else:
            self._cursor_mode = "BOOTSTRAP"
            self._cursor_value = 0
            self._last_updated_at = self.sync_from_date

    # --- Dynamic schema ---

    def get_json_schema(self) -> Mapping[str, Any]:
        """Build JSON Schema dynamically from Tulip table metadata."""
        properties: Dict[str, Any] = {}

        # System fields
        for field_name, schema in SYSTEM_FIELDS_SCHEMA.items():
            properties[field_name] = schema.copy()

        # Custom fields from table metadata
        for field in self._table_metadata.get("columns", []):
            field_id = field["name"]
            if field_id in SYSTEM_FIELD_NAMES:
                continue

            tulip_type = field.get("dataType", {}).get("type", "string")

            # Exclude tableLink fields
            if tulip_type == "tableLink":
                continue

            field_label = field.get("label", "")
            column_name = generate_column_name(field_id, field_label)
            properties[column_name] = map_tulip_type_to_json_schema(tulip_type)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }

    # --- Field mapping (lazy init) ---

    def _get_field_mapping(self) -> Dict[str, str]:
        if self._field_mapping is None:
            self._field_mapping = build_field_mapping(self._table_metadata)
        return self._field_mapping

    def _get_allowed_fields(self) -> List[str]:
        if self._allowed_fields is None:
            self._allowed_fields = build_allowed_fields(self._table_metadata)
        return self._allowed_fields

    def _commit_cursor(self) -> None:
        """Commit the max seen _updatedAt to the durable cursor.

        Called only when a sync completes (last batch processed). This
        ensures mid-run checkpoints and filter construction use the
        frozen start-of-sync value, preventing data loss on crash and
        incorrect pagination filters.
        """
        if self._max_seen_updated_at:
            self._last_updated_at = self._max_seen_updated_at
            self._max_seen_updated_at = None

    # --- HTTP request configuration ---

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """Build query params with filters, sort, limit, fields."""
        if self._cursor_mode == "BOOTSTRAP":
            # BOOTSTRAP: cursor-based pagination via _sequenceNumber
            if next_page_token:
                last_sequence = next_page_token["last_sequence"]
            else:
                last_sequence = self._cursor_value
            api_filters = self._build_bootstrap_filters(last_sequence)
        else:
            # INCREMENTAL: _updatedAt is the between-sync cursor.
            # _sequenceNumber is only used for pagination within a sync run.
            api_filters = self._build_incremental_filters()
            if next_page_token:
                api_filters.append(
                    {
                        "field": "_sequenceNumber",
                        "functionType": "greaterThan",
                        "arg": next_page_token["last_sequence"],
                    }
                )

        return {
            "limit": DEFAULT_LIMIT,
            "offset": 0,
            "filters": json.dumps(api_filters),
            "sortOptions": json.dumps(
                [{"sortBy": "_sequenceNumber", "sortDir": "asc"}]
            ),
            "fields": json.dumps(self._get_allowed_fields()),
        }

    def _build_bootstrap_filters(self, last_sequence: int) -> List[Dict[str, Any]]:
        """Build filters for bootstrap phase."""
        api_filters: List[Dict[str, Any]] = [
            {
                "field": "_sequenceNumber",
                "functionType": "greaterThan",
                "arg": last_sequence,
            }
        ]
        if self.sync_from_date:
            api_filters.append(
                {
                    "field": "_updatedAt",
                    "functionType": "greaterThan",
                    "arg": self.sync_from_date,
                }
            )
        api_filters.extend(self.custom_filters)
        return api_filters

    def _build_incremental_filters(self) -> List[Dict[str, Any]]:
        """Build filters for incremental phase using _updatedAt with 60s lookback.

        Unlike BOOTSTRAP, INCREMENTAL does NOT filter on _sequenceNumber because
        updated records keep their original _sequenceNumber. Using _updatedAt as
        the sole between-sync cursor ensures both new and updated records are captured.
        _sequenceNumber is only added for pagination (via next_page_token) within a
        single sync run.
        """
        api_filters: List[Dict[str, Any]] = []
        start_time = adjust_cursor_for_overlap(self._last_updated_at)
        if start_time:
            api_filters.append(
                {
                    "field": "_updatedAt",
                    "functionType": "greaterThan",
                    "arg": start_time,
                }
            )
        api_filters.extend(self.custom_filters)
        return api_filters

    # --- Pagination ---

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        """Cursor-based pagination using _sequenceNumber."""
        records = response.json()
        if not records or len(records) < DEFAULT_LIMIT:
            return None
        last_record = records[-1]
        return {"last_sequence": last_record.get("_sequenceNumber")}

    # --- Response parsing ---

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Transform records: map field IDs to human-readable column names."""
        field_mapping = self._get_field_mapping()
        records = response.json()

        if not records:
            if self._cursor_mode == "BOOTSTRAP":
                logger.info(
                    f"Stream {self.name}: BOOTSTRAP complete "
                    f"(empty batch), switching to INCREMENTAL"
                )
                self._cursor_mode = "INCREMENTAL"
            self._commit_cursor()
            return

        for record in records:
            # Track cursor values
            seq = record.get("_sequenceNumber")
            if seq is not None and seq > self._cursor_value:
                self._cursor_value = seq

            updated_at = record.get("_updatedAt")
            if updated_at and (
                not self._max_seen_updated_at or updated_at > self._max_seen_updated_at
            ):
                self._max_seen_updated_at = updated_at

            yield transform_record(record, field_mapping)

        # Detect last batch (sync completion) and commit cursor
        is_last_batch = len(records) < DEFAULT_LIMIT

        if self._cursor_mode == "BOOTSTRAP" and is_last_batch:
            logger.info(
                f"Stream {self.name}: BOOTSTRAP complete "
                f"(batch had {len(records)} records < {DEFAULT_LIMIT}), "
                f"switching to INCREMENTAL"
            )
            self._cursor_mode = "INCREMENTAL"
            self._commit_cursor()
        elif self._cursor_mode == "INCREMENTAL" and is_last_batch:
            self._commit_cursor()

    @property
    def http_method(self) -> str:
        return "GET"
