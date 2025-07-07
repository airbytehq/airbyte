#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
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
    Transforms the input state for per-partitioned streams from the legacy format to the low-code global cursor format.

    Example input state:
    {
      "1234567890": {"segments.date": "2120-10-10"}
    }
    Example output state:
    {
      "state": {"use_global_cursor": True, "segments.date": "2120-10-10"}
    }
    """

    config: Config

    def __init__(self, config: Config):
        self._config = config
        self._cursor_field = "segments.date"

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state and "state" not in stream_state

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
        return {"use_global_cursor": True, "state": min_state}
