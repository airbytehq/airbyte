#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import copy
import json
import logging
import re
from dataclasses import dataclass
from itertools import groupby
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import anyascii
import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.incremental import (
    CursorFactory,
    DatetimeBasedCursor,
    GlobalSubstreamCursor,
    PerPartitionWithGlobalCursor,
)
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema.inline_schema_loader import InlineSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


logger = logging.getLogger("airbyte")

REPORT_MAPPING = {
    "account_performance_report": "customer",
    "ad_group_ad_legacy": "ad_group_ad",
    "ad_group_bidding_strategy": "ad_group",
    "ad_listing_group_criterion": "ad_group_criterion",
    "campaign_real_time_bidding_settings": "campaign",
    "campaign_bidding_strategy": "campaign",
    "service_accounts": "customer",
}


class AccessibleAccountsExtractor(RecordExtractor):
    """
    Custom extractor for the accessible accounts endpoint.
    The response is a list of strings instead of a list of objects.
    """

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        response_data = response.json().get("resourceNames", [])
        if response_data:
            for resource_name in response_data:
                yield {"accessible_customer_id": resource_name.split("/")[-1]}


@dataclass
class CustomerClientFilter(RecordFilter):
    """
    Filter duplicated records based on the "clientCustomer" field.
    This can happen when customer client account may be accessible from multiple customer client accounts.
    """

    UNIQUE_KEY = "clientCustomer"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._seen_keys = set()

    def filter_records(
        self, records: List[Mapping[str, Any]], stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for record in records:
            # Filter out records based on customer_ids if provided in the config
            if self.config.get("customer_ids") and (record["id"] not in self.config["customer_ids"]):
                continue

            # Filter out records based on customer status if provided in the config
            if record["status"] not in (
                self.config.get("customer_status_filter") or ["UNKNOWN", "ENABLED", "CANCELED", "SUSPENDED", "CLOSED"]
            ):
                continue

            key = record[self.UNIQUE_KEY]
            if key not in self._seen_keys:
                self._seen_keys.add(key)
                yield record


@dataclass
class FlattenNestedDictsTransformation(RecordTransformation):
    """
    Recursively flattens all nested dictionary fields in a record into top-level keys
    using dot-separated paths, skipping dictionaries inside lists, and removes
    the original nested dictionary fields.

    Example:
      {"a": {"b": 1, "c": {"d": 2}, "e": [ {"f": 3} ]}, "g": [{"h": 4}]}
    becomes:
      {"a.b": 1, "a.c.d": 2, "a.e": [ {"f": 3} ], "g": [{"h": 4}]}
    """

    delimiter: str = "."

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        def _flatten(prefix: str, obj: Dict[str, Any]):
            for key, value in list(obj.items()):
                new_key = f"{prefix}{self.delimiter}{key}" if prefix else key
                if isinstance(value, dict):
                    # recurse into nested dict
                    _flatten(new_key, value)
                else:
                    # set flattened value at top level
                    record[new_key] = value

        # find all top-level dict fields (skip dicts in lists)
        for top_key in [k for k, v in list(record.items()) if isinstance(v, dict)]:
            nested = record.pop(top_key)
            _flatten(top_key, nested)


class DoubleQuotedDictTypeTransformer(TypeTransformer):
    """
    Convert arrays of dicts into JSON-formatted string arrays using double quotes only
    when the schema defines a (nullable) array of strings. Output strings use no spaces
    after commas and a single space after colons for consistent formatting.

    Example:
      [{'key': 'campaign', 'value': 'gg_nam_dg_search_brand'}]
    → ['{"key": "campaign","value": "gg_nam_dg_search_brand"}']
    """

    def __init__(self, *args, **kwargs):
        # apply this transformer during schema normalization phase(s)
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        # register our custom transform
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            # Skip null values (schema may include 'null')
            if original_value is None:
                return original_value

            # Only apply if schema type includes 'array'
            schema_type = field_schema.get("type")
            if isinstance(schema_type, list):
                if "array" not in schema_type:
                    return original_value
            elif schema_type != "array":
                return original_value

            # Only apply if items type includes 'string'
            items = field_schema.get("items", {}) or {}
            items_type = items.get("type")
            if isinstance(items_type, list):
                if "string" not in items_type:
                    return original_value
            elif items_type != "string":
                return original_value

            # Transform only lists where every element is a dict
            if isinstance(original_value, list) and all(isinstance(el, dict) for el in original_value):
                return [json.dumps(el, separators=(",", ": ")) for el in original_value]

            return original_value

        return transform_function


class GoogleAdsPerPartitionStateMigration(StateMigration):
    """
    Migrates legacy per-partition Google Ads state to low code format
    that includes parent_slice for each customer_id partition.


    Example input state:
    {
      "1234567890": {"segments.date": "2120-10-10"},
      "0987654321": {"segments.date": "2120-10-11"}
    }
    Example output state:
    {
      "states": [
        {
            "partition": { "customer_id": "1234567890", "parent_slice": {"customer_id": "1234567890_parent", "parent_slice": {}}},
            "cursor": {"segments.date": "2120-10-10"}
        },
        {
            "partition": { "customer_id": "0987654321", "parent_slice": {"customer_id": "0987654321_parent", "parent_slice": {}}},
            "cursor": {"segments.date": "2120-10-11"}
        }
      ],
      "state": {"segments.date": "2120-10-10"}
    }
    """

    config: Config
    customer_client_stream: DeclarativeStream
    cursor_field: str = "segments.date"

    def __init__(self, config: Config, customer_client_stream: DeclarativeStream, cursor_field: str = "segments.date"):
        self._config = config
        self._parent_stream = customer_client_stream
        self._cursor_field = cursor_field

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state and "state" not in stream_state

    def _read_parent_stream(self) -> Iterable[Tuple[Mapping[str, Any], StreamSlice]]:
        # iterate all slices of the customer_client stream
        slices = self._parent_stream.stream_slices(sync_mode=SyncMode.full_refresh)

        for slice in slices:
            for record in self._parent_stream.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh):
                yield record, slice

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state

        stream_state_values = [
            stream_state for stream_state in stream_state.values() if isinstance(stream_state, dict) and self._cursor_field in stream_state
        ]
        if not stream_state_values:
            logger.warning("No valid cursor field found in the stream state. Returning empty state.")
            return {}

        min_state = min(stream_state_values, key=lambda state: state[self._cursor_field])

        customer_ids_in_state = list(stream_state.keys())

        partitions_state = []

        for record, slice in self._read_parent_stream():
            customer_id = record.get("id")
            if customer_id in customer_ids_in_state:
                legacy_partition_state = stream_state[customer_id]

                partitions_state.append(
                    {
                        "partition": {
                            "customer_id": record["clientCustomer"],
                            "parent_slice": {"customer_id": slice.get("customer_id"), "parent_slice": {}},
                        },
                        "cursor": legacy_partition_state,
                    }
                )

        if not partitions_state:
            logger.warning("No matching customer clients found during state migration.")
            return {}

        state = {"states": partitions_state, "state": min_state}
        return state


@dataclass
class GoogleAdsHttpRequester(HttpRequester):
    """
    Custom HTTP requester for Google Ads API that uses the accessible accounts endpoint
    to retrieve the list of accessible customer IDs.
    """

    schema_loader: InlineSchemaLoader = None

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        schema = self.schema_loader.get_json_schema()[self.name]["properties"]
        manager = stream_slice.extra_fields.get("manager", False)
        resource_name = REPORT_MAPPING.get(self.name, self.name)
        fields = [
            field
            for field in schema.keys()
            # exclude metrics.* if this is a manager account
            if not (manager and field.startswith("metrics."))
        ]

        if "start_time" in stream_slice and "end_time" in stream_slice:
            # For incremental streams
            query = f"SELECT {', '.join(fields)} FROM {resource_name} WHERE segments.date BETWEEN '{stream_slice['start_time']}' AND '{stream_slice['end_time']}' ORDER BY segments.date ASC"
        else:
            # For full refresh streams
            query = f"SELECT {', '.join(fields)} FROM {resource_name}"

        return {"query": query}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {
            "developer-token": self.config["credentials"]["developer_token"],
            "login-customer-id": stream_slice["parent_slice"]["customer_id"],
        }


@dataclass
class ClickViewHttpRequester(GoogleAdsHttpRequester):
    """
    Custom HTTP requester for ClickView stream.
    """

    schema_loader: InlineSchemaLoader = None

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        schema = self.schema_loader.get_json_schema()["properties"]
        fields = [field for field in schema.keys()]
        return {"query": f"SELECT {', '.join(fields)} FROM click_view WHERE segments.date = '{stream_slice['start_time']}'"}


@dataclass
class KeysToSnakeCaseGoogleAdsTransformation(RecordTransformation):
    """
    Transforms keys in a Google Ads record to snake_case.
    The difference with KeysToSnakeCaseTransformation is that this transformation doesn't add underscore before digits.
    """

    token_pattern: re.Pattern[str] = re.compile(
        r"""
            \d*[A-Z]+[a-z]*\d*        # uppercase word (with optional leading/trailing digits)
          | \d*[a-z]+\d*              # lowercase word (with optional leading/trailing digits)
          | (?P<NoToken>[^a-zA-Z\d]+) # any non-alphanumeric separators
        """,
        re.VERBOSE,
    )

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        transformed_record = self._transform_record(record)
        record.clear()
        record.update(transformed_record)

    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        transformed_record = {}
        for key, value in record.items():
            transformed_key = self.process_key(key)
            transformed_value = value

            if isinstance(value, dict):
                transformed_value = self._transform_record(value)

            transformed_record[transformed_key] = transformed_value
        return transformed_record

    def process_key(self, key: str) -> str:
        key = self.normalize_key(key)
        tokens = self.tokenize_key(key)
        tokens = self.filter_tokens(tokens)
        return self.tokens_to_snake_case(tokens)

    def normalize_key(self, key: str) -> str:
        return str(anyascii.anyascii(key))

    def tokenize_key(self, key: str) -> List[str]:
        tokens = []
        for match in self.token_pattern.finditer(key):
            token = match.group(0) if match.group("NoToken") is None else ""
            tokens.append(token)
        return tokens

    def filter_tokens(self, tokens: List[str]) -> List[str]:
        if len(tokens) >= 3:
            tokens = tokens[:1] + [t for t in tokens[1:-1] if t] + tokens[-1:]
        return tokens

    def tokens_to_snake_case(self, tokens: List[str]) -> str:
        return "_".join(token.lower() for token in tokens)


@dataclass
class ChangeStatusRetriever(SimpleRetriever):
    """
    Retrieves change status records from the Google Ads API.
    ChangeStatus stream requires custom retriever because Google Ads API requires limit for this stream to be set to 10,000.
    When the number of records exceeds this limit, we need to adjust the start date to the last record's cursor.
    """

    partition_router: SubstreamPartitionRouter = None
    transformations: List[RecordTransformation] = None
    QUERY_LIMIT = 10000
    cursor_field: str = "change_status.last_change_date_time"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        original_cursor: DatetimeBasedCursor = self.stream_slicer

        cursor_for_factory = copy.deepcopy(original_cursor)
        cursor_for_stream = copy.deepcopy(original_cursor)

        self.stream_slicer = PerPartitionWithGlobalCursor(
            cursor_factory=CursorFactory(lambda: copy.deepcopy(cursor_for_factory)),
            partition_router=self.partition_router,
            stream_cursor=cursor_for_stream,
        )

        self.cursor = self.stream_slicer

        self.record_selector.transformations = self.transformations

    def _read_pages(
        self,
        records_generator_fn: Callable[[Optional[Mapping]], Iterable[Record]],
        stream_state: StreamState,
        stream_slice: StreamSlice,
    ) -> Iterable[Record]:
        """
        Since this stream doesn’t support “real” pagination, we treat each HTTP
        call as a slice defined by a start_date / end_date. If we hit the
        QUERY_LIMIT exactly, we assume there may be more data at the end of that
        slice, so we bump start_date forward to the last-record cursor and retry.
        """
        while True:
            record_count = 0
            last_record = None
            response = self._fetch_next_page(stream_state, stream_slice)

            # Yield everything we got
            for rec in records_generator_fn(response):
                record_count += 1
                last_record = rec
                yield rec

            if record_count < self.QUERY_LIMIT:
                break

            # Update the stream slice start time to the last record's cursor
            last_cursor = last_record[self.cursor_field]
            cursor_slice = stream_slice.cursor_slice
            cursor_slice["start_time"] = last_cursor
            stream_slice = StreamSlice(
                partition=stream_slice.partition,
                cursor_slice=cursor_slice,
                extra_fields=stream_slice.extra_fields,
            )


@dataclass
class ChangeStatusRequester(GoogleAdsHttpRequester):
    CURSOR_FIELD: str = "change_status.last_change_date_time"
    LIMIT: int = 10000

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._resource_type = (parameters or {}).get("resource_type")

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        schema = self.schema_loader.get_json_schema()[self.name]["properties"]
        fields = list(schema.keys())

        query = (
            f"SELECT {', '.join(fields)} FROM {self.name} "
            f"WHERE {self.CURSOR_FIELD} BETWEEN '{stream_slice['start_time']}' AND '{stream_slice['end_time']}' "
            f"AND change_status.resource_type = {self._resource_type} "
            f"ORDER BY {self.CURSOR_FIELD} ASC "
            f"LIMIT {self.LIMIT}"
        )
        return {"query": query}


@dataclass
class CriterionRetriever(SimpleRetriever):
    """
    Retrieves Criterion records based on ChangeStatus updates.

    For each parent_slice:
      1) Emits a “deleted” record for any REMOVED status.
      2) Batches the remaining IDs into a single fetch.
      3) Attaches the original ChangeStatus timestamp to each returned record.
    """

    partition_router: SubstreamPartitionRouter = None
    transformations: List[RecordTransformation] = None
    cursor_field: str = "change_status.last_change_date_time"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)

        original_cursor: DatetimeBasedCursor = self.stream_slicer

        cursor_for_stream = copy.deepcopy(original_cursor)

        self.stream_slicer = GlobalSubstreamCursor(
            partition_router=self.partition_router,
            stream_cursor=cursor_for_stream,
        )

        self.cursor = self.stream_slicer

        self.record_selector.transformations = self.transformations

    def _read_pages(
        self,
        records_generator_fn: Callable[[Optional[Mapping]], Iterable[Record]],
        stream_state: StreamState,
        stream_slice: StreamSlice,
    ) -> Iterable[Record]:
        """
        Emit deletions and then fetch updates grouped by parent_slice:
        - GROUP records by parent (zip ids, parents, statuses, times).
        - For each group, yield REMOVED records immediately, then perform one fetch for non-removed.
        - Attach the original ChangeStatus timestamp to each updated record.
        """
        ids = stream_slice.partition[self.primary_key[0]]
        parents = stream_slice.partition["parent_slice"]
        statuses = stream_slice.extra_fields["change_status.resource_status"]
        times = stream_slice.extra_fields["change_status.last_change_date_time"]

        # Iterate grouped by parent
        for parent, group in groupby(
            zip(ids, parents, statuses, times),
            key=lambda x: x[1],
        ):
            group_list = list(group)
            # Emit deletions first
            updated_ids = []
            updated_times = []
            for _id, _, status, ts in group_list:
                if status == "REMOVED":
                    yield Record(
                        data={
                            self.primary_key[0]: _id,
                            "deleted_at": ts,
                        },
                        stream_name=self.name,
                    )
                else:
                    updated_ids.append(_id)
                    updated_times.append(ts)

            # Single fetch for non-removed
            if not updated_ids:
                continue
            # build time map for updated records
            time_map = dict(zip(updated_ids, updated_times))
            new_slice = StreamSlice(
                partition={
                    self.primary_key[0]: updated_ids,
                    "parent_slice": parent,
                },
                cursor_slice=stream_slice.cursor_slice,
                extra_fields={"change_status.last_change_date_time": updated_times},
            )
            response = self._fetch_next_page(stream_state, new_slice)
            for rec in records_generator_fn(response):
                # attach timestamp from ChangeStatus
                rec.data[self.cursor_field] = time_map.get(rec.data.get(self.primary_key[0]))
                yield rec


@dataclass
class CriterionIncrementalRequester(GoogleAdsHttpRequester):
    CURSOR_FIELD: str = "change_status.last_change_date_time"

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        props = self.schema_loader.get_json_schema()[self.name]["properties"]
        select_fields = [f for f in props.keys() if f not in (self.CURSOR_FIELD, "deleted_at")]

        ids = stream_slice.partition.get(self._parameters["primary_key"][0], [])
        in_list = ", ".join(f"'{i}'" for i in ids)

        query = (
            f"SELECT {', '.join(select_fields)}\n"
            f"  FROM {self._parameters['resource_name']}\n"
            f" WHERE {self._parameters['primary_key'][0]} IN ({in_list})\n"
        )

        return {"query": query}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, any]] = None,
    ) -> Mapping[str, any]:
        return {
            "developer-token": self.config["credentials"]["developer_token"],
            "login-customer-id": stream_slice["parent_slice"]["parent_slice"]["customer_id"],
        }


@dataclass
class CriterionFullRefreshRequester(GoogleAdsHttpRequester):
    CURSOR_FIELD: str = "change_status.last_change_date_time"

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        props = self.schema_loader.get_json_schema()[self.name]["properties"]
        fields = [f for f in props.keys() if f not in (self.CURSOR_FIELD, "deleted_at")]

        return {"query": f"SELECT {', '.join(fields)} FROM {self._parameters['resource_name']}"}


class GoogleAdsCriterionParentStateMigration(StateMigration):
    """
    Migrates parent state from legacy format to the new format
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state and "parent_state" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state

        return {"parent_state": stream_state}
