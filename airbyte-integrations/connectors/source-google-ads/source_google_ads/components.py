#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import anyascii
import requests

from airbyte_cdk import InterpolatedString
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.schema import DynamicSchemaLoader, SchemaLoader
from airbyte_cdk.sources.declarative.schema.inline_schema_loader import InlineSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
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

DATE_TYPES = ("segments.date", "segments.month", "segments.quarter", "segments.week")


GOOGLE_ADS_DATATYPE_MAPPING = {
    "INT64": "integer",
    "INT32": "integer",
    "DOUBLE": "number",
    "STRING": "string",
    "BOOLEAN": "boolean",
    "DATE": "string",
    "MESSAGE": "string",
    "ENUM": "string",
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
class CustomGAQueryHttpRequester(HttpRequester):
    """
    Custom HTTP requester for custom query streams.
    """

    query: str = ""
    primary_key: Optional[List[str]] = None
    cursor_field: Union[str, InterpolatedString] = ""

    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters=parameters)
        self._cursor_field = InterpolatedString.create(self.cursor_field, parameters={})

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        query = self._build_query(stream_slice)
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

    def _build_query(self, stream_slice: StreamSlice) -> str:
        fields = self._get_list_of_fields()
        resource_name = self._get_resource_name()

        cursor_field = self._cursor_field.eval(self.config)

        if cursor_field:
            fields.append(cursor_field)

        if "start_time" in stream_slice and "end_time" in stream_slice and cursor_field:
            query = f"SELECT {', '.join(fields)} FROM {resource_name} WHERE {cursor_field} BETWEEN '{stream_slice['start_time']}' AND '{stream_slice['end_time']}' ORDER BY {self.cursor_field} ASC"
        else:
            query = f"SELECT {', '.join(fields)} FROM {resource_name}"
        return query

    def _get_list_of_fields(self) -> List[str]:
        """
        Extract field names from the `SELECT` clause of the query.
        e.g. Parses a query "SELECT field1, field2, field3 FROM table" and returns ["field1", "field2", "field3"].
        """
        query_upper = self.query.upper()
        select_index = query_upper.find("SELECT")
        from_index = query_upper.find("FROM")

        fields_portion = self.query[select_index + 6 : from_index].strip()

        fields = [field.strip() for field in fields_portion.split(",")]

        return fields

    def _get_resource_name(self) -> str:
        """
        Extract the resource name from the `FROM` clause of the query.
        e.g. Parses a query "SELECT field1, field2, field3 FROM table" and returns "table".
        """
        query_upper = self.query.upper()
        from_index = query_upper.find("FROM")
        return self.query[from_index + 4 :].strip()


@dataclass()
class CustomGAQuerySchemaLoader(SchemaLoader):
    """
    Custom schema loader for custom query streams. Parses the user-provided query to extract the fields and then queries the Google Ads API for each field to retreive field metadata.
    """

    requester: HttpRequester
    config: Config

    query: str = ""
    cursor_field: Union[str, InterpolatedString] = ""

    def __post_init__(self):
        self._cursor_field = InterpolatedString.create(self.cursor_field, parameters={})

    def get_json_schema(self) -> Dict[str, Any]:
        local_json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

        fields = self._get_list_of_fields()
        cursor_field = self._cursor_field.eval(self.config)
        if cursor_field:
            fields.append(cursor_field)

        for field in fields:
            response = requests.get(
                url=f"https://googleads.googleapis.com/v18/googleAdsFields/{field}",
                headers=self._get_request_headers(),
            )
            response.raise_for_status()
            response_json = response.json()

            field_value = self._build_field_value(field, response_json)
            local_json_schema["properties"][field] = field_value

        return local_json_schema

    def _build_field_value(self, field: str, response_json: Dict[str, Any]) -> Any:
        field_value = {"type": [GOOGLE_ADS_DATATYPE_MAPPING.get(response_json["dataType"], response_json["dataType"]), "null"]}

        if response_json["dataType"] == "DATE" and field in DATE_TYPES:
            field_value["format"] = "date"

        if response_json["dataType"] == "ENUM":
            field_value["enum"] = [value for value in response_json["enumValues"]]

        if response_json["isRepeated"]:
            field_value = {"type": ["null", "array"], "items": field_value}

        return field_value

    def _get_list_of_fields(self) -> List[str]:
        """
        Extract field names from the `SELECT` clause of the query.
        e.g. Parses a query "SELECT field1, field2, field3 FROM table" and returns ["field1", "field2", "field3"].
        """
        query_upper = self.query.upper()
        select_index = query_upper.find("SELECT")
        from_index = query_upper.find("FROM")

        fields_portion = self.query[select_index + 6 : from_index].strip()

        fields = [field.strip() for field in fields_portion.split(",")]

        return fields

    def _get_request_headers(self) -> Mapping[str, Any]:
        headers = {}
        auth_headers = self.requester.authenticator.get_auth_header()
        if auth_headers:
            headers.update(auth_headers)

        headers["developer-token"] = self.config["credentials"]["developer_token"]
        return headers
