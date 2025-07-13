#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.schema.inline_schema_loader import InlineSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


logger = logging.getLogger("airbyte")


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

    def __init__(self, config: Config, customer_client_stream: DeclarativeStream):
        self._config = config
        self._parent_stream = customer_client_stream
        self._cursor_field = "segments.date"

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
        fields = [
            field
            for field in schema.keys()
            # exclude metrics.* if this is a manager account
            if not (manager and field.startswith("metrics."))
        ]
        return {
            "query": f"SELECT {', '.join(fields)} FROM {self.name} WHERE segments.date BETWEEN '{stream_slice['start_time']}' AND '{stream_slice['end_time']}' ORDER BY segments.date ASC"
        }

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
