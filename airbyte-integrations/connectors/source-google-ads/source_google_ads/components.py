#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
import re
import threading
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any, Callable, Dict, Generator, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import anyascii
import requests

from airbyte_cdk import AirbyteTracedException, FailureType, InterpolatedString
from airbyte_cdk.sources.declarative.decoders.composite_raw_decoder import JsonParser
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema import SchemaLoader
from airbyte_cdk.sources.declarative.schema.inline_schema_loader import InlineSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .google_ads import GoogleAds


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
    "RESOURCE_NAME": "string",
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
            # Convert record["id"] to string for comparison since customer_ids are parsed as strings
            if self.config.get("customer_ids") and (str(record["id"]) not in self.config["customer_ids"]):
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
    customer_client_stream: DefaultStream
    cursor_field: str = "segments.date"

    def __init__(self, config: Config, customer_client_stream: DefaultStream, cursor_field: str = "segments.date"):
        self._config = config
        self._parent_stream = customer_client_stream
        self._cursor_field = cursor_field

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state and "state" not in stream_state

    def _read_parent_stream(self) -> Iterable[Record]:
        for partition in self._parent_stream.generate_partitions():
            for record in partition.read():
                yield record

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

        for record in self._read_parent_stream():
            customer_id = record.data.get("id")
            if customer_id in customer_ids_in_state:
                legacy_partition_state = stream_state[customer_id]

                partitions_state.append(
                    {
                        "partition": {
                            "customer_id": record["clientCustomer"],
                            "parent_slice": {"customer_id": record.associated_slice.get("customer_id"), "parent_slice": {}},
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

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.stream_response = True

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

    cursor_field: str = "change_status.last_change_date_time"

    def _read_pages(
        self,
        records_generator_fn: Callable[[Optional[Mapping]], Iterable[Record]],
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
                        associated_slice=stream_slice,
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
            response = self._fetch_next_page(new_slice)
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
        return stream_state and not stream_state.get("parent_state")

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state

        return {"parent_state": {"change_status": stream_state}}


class GoogleAdsGlobalStateMigration(StateMigration):
    """
    Migrates global state to include use_global_cursor key. Previously legacy GlobalSubstreamCursor was used.
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state and not stream_state.get("use_global_cursor")

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        stream_state["use_global_cursor"] = True
        return stream_state


@dataclass(repr=False, eq=False, frozen=True)
class GAQL:
    """
    Simple regex parser of Google Ads Query Language
    https://developers.google.com/google-ads/api/docs/query/grammar
    """

    fields: Tuple[str]
    resource_name: str
    where: str
    order_by: str
    limit: Optional[int]
    parameters: str

    REGEX = re.compile(
        r"""\s*
            SELECT\s+(?P<FieldNames>\S.*)
            \s+
            FROM\s+(?P<ResourceNames>[a-z][a-zA-Z_]*(\s*,\s*[a-z][a-zA-Z_]*)*)
            \s*
            (\s+WHERE\s+(?P<WhereClause>\S.*?))?
            (\s+ORDER\s+BY\s+(?P<OrderByClause>\S.*?))?
            (\s+LIMIT\s+(?P<LimitClause>[1-9]([0-9])*))?
            \s*
            (\s+PARAMETERS\s+(?P<ParametersClause>\S.*?))?
            $""",
        flags=re.I | re.DOTALL | re.VERBOSE,
    )

    REGEX_FIELD_NAME = re.compile(r"^[a-z][a-z0-9._]*$", re.I)

    @classmethod
    def parse(cls, query):
        m = cls.REGEX.match(query)
        if not m:
            raise ValueError

        fields = [f.strip() for f in m.group("FieldNames").split(",")]
        for field in fields:
            if not cls.REGEX_FIELD_NAME.match(field):
                raise ValueError

        resource_names = re.split(r"\s*,\s*", m.group("ResourceNames"))
        if len(resource_names) > 1:
            raise ValueError
        resource_name = resource_names[0]

        where = cls._normalize(m.group("WhereClause") or "")
        order_by = cls._normalize(m.group("OrderByClause") or "")
        limit = m.group("LimitClause")
        if limit:
            limit = int(limit)
        parameters = cls._normalize(m.group("ParametersClause") or "")
        return cls(tuple(fields), resource_name, where, order_by, limit, parameters)

    def __str__(self):
        fields = ", ".join(self.fields)
        query = f"SELECT {fields} FROM {self.resource_name}"
        if self.where:
            query += " WHERE " + self.where
        if self.order_by:
            query += " ORDER BY " + self.order_by
        if self.limit is not None:
            query += " LIMIT " + str(self.limit)
        if self.parameters:
            query += " PARAMETERS " + self.parameters
        return query

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _normalize(s):
        s = s.strip()
        return re.sub(r"\s+", " ", s)

    def set_where(self, value: str):
        return self.__class__(self.fields, self.resource_name, value, self.order_by, self.limit, self.parameters)

    def set_limit(self, value: int):
        return self.__class__(self.fields, self.resource_name, self.where, self.order_by, value, self.parameters)

    def append_field(self, value):
        fields = list(self.fields)
        fields.append(value)
        return self.__class__(tuple(fields), self.resource_name, self.where, self.order_by, self.limit, self.parameters)


class CustomGAQueryHttpRequester(HttpRequester):
    """
    Custom HTTP requester for custom query streams.
    """

    parameters: Mapping[str, Any]

    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters=parameters)
        self.query = GAQL.parse(parameters.get("query"))
        self.stream_response = True

    @staticmethod
    def is_metrics_in_custom_query(query: GAQL) -> bool:
        for field in query.fields:
            if field.split(".")[0] == "metrics":
                return True
        return False

    @staticmethod
    def is_custom_query_incremental(query: GAQL) -> bool:
        time_segment_in_select, time_segment_in_where = ["segments.date" in clause for clause in [query.fields, query.where]]
        return time_segment_in_select and not time_segment_in_where

    @staticmethod
    def _insert_segments_date_expr(query: GAQL, start_date: str, end_date: str) -> GAQL:
        if "segments.date" not in query.fields:
            query = query.append_field("segments.date")
        condition = f"segments.date BETWEEN '{start_date}' AND '{end_date}'"
        if query.where:
            return query.set_where(query.where + " AND " + condition)
        return query.set_where(condition)

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
        is_incremental = self.is_custom_query_incremental(self.query)

        if is_incremental:
            start_date = stream_slice["start_time"]
            end_date = stream_slice["end_time"]
            return str(self._insert_segments_date_expr(self.query, start_date, end_date))
        else:
            return str(self.query)

    def _get_resource_name(self) -> str:
        """
        Extract the resource name from the `FROM` clause of the query.
        e.g. Parses a query "SELECT field1, field2, field3 FROM table" and returns "table".
        """
        query_upper = self.query.upper()
        from_index = query_upper.find("FROM")
        return self.query[from_index + 4 :].strip()


class CustomGAQueryClickViewHttpRequester(CustomGAQueryHttpRequester):
    @staticmethod
    def _insert_segments_date_expr(query: GAQL, start_date: str, end_date: str) -> GAQL:
        if "segments.date" not in query.fields:
            query = query.append_field("segments.date")
        condition = f"segments.date ='{start_date}'"
        if query.where:
            return query.set_where(query.where + " AND " + condition)
        return query.set_where(condition)


@dataclass()
class CustomGAQuerySchemaLoader(SchemaLoader):
    """
    Custom schema loader for custom query streams. Parses the user-provided query to extract the fields and then queries the Google Ads API for each field to retreive field metadata.
    """

    config: Config

    query: str = ""
    cursor_field: Union[str, InterpolatedString] = ""

    _google_ads_client: Optional[GoogleAds] = None
    _client_lock = threading.Lock()

    def __post_init__(self):
        self._cursor_field = InterpolatedString.create(self.cursor_field, parameters={}) if self.cursor_field else None
        self._validate_query(self.query)

    @classmethod
    def google_ads_client(cls, config: Config) -> GoogleAds:
        """
        Lazily creates a single GoogleAds client shared by all instances of this class.
        First call wins (its config is used).
        """
        if cls._google_ads_client is None:
            with cls._client_lock:
                if cls._google_ads_client is None:
                    cls._google_ads_client = GoogleAds(credentials=cls.get_credentials(config))
        return cls._google_ads_client

    @staticmethod
    def get_credentials(config: Mapping[str, Any]) -> MutableMapping[str, Any]:
        credentials = config["credentials"]
        # use_proto_plus is set to True, because setting to False returned wrong value types, which breaks the backward compatibility.
        # For more info read the related PR's description: https://github.com/airbytehq/airbyte/pull/9996
        credentials.update(use_proto_plus=True)
        return credentials

    def get_json_schema(self) -> Dict[str, Any]:
        local_json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

        fields = self._get_list_of_fields()
        fields_metadata = self.google_ads_client(self.config).get_fields_metadata(fields)

        for field, field_metadata in fields_metadata.items():
            field_value = self._build_field_value(field, field_metadata)
            local_json_schema["properties"][field] = field_value

        return local_json_schema

    def _build_field_value(self, field: str, field_metadata) -> Any:
        # Data type return in enum format: "GoogleAdsFieldDataType.<data_type>"
        google_data_type = field_metadata.data_type.name
        field_value = {"type": [GOOGLE_ADS_DATATYPE_MAPPING.get(google_data_type, "string"), "null"]}

        # Google Ads doesn't differentiate between DATE and DATETIME, so we need to manually check for fields with known type
        if google_data_type == "DATE" and field in DATE_TYPES:
            field_value["format"] = "date"

        if google_data_type == "ENUM":
            field_value = {"type": "string", "enum": list(field_metadata.enum_values)}

        if field_metadata.is_repeated:
            field_value = {"type": ["null", "array"], "items": field_value}

        return field_value

    def _get_list_of_fields(self) -> List[str]:
        """
        Extract field names from the `SELECT` clause of the query.
        e.g. Parses a query "SELECT field1, field2, field3 FROM table" and returns ["field1", "field2", "field3"].
        """
        query_upper = self.query.upper()
        select_index = query_upper.find("SELECT")
        match = re.search(r"\bFROM\b", query_upper)
        if not match:
            raise ValueError("Could not find a valid FROM clause in query")
        from_index = match.start()

        fields_portion = self.query[select_index + 6 : from_index].strip()

        fields = [field.strip() for field in fields_portion.split(",")]

        cursor_field = self._cursor_field.eval(self.config) if self._cursor_field else None
        if cursor_field:
            fields.append(cursor_field)

        return fields

    def _validate_query(self, query: str):
        try:
            GAQL.parse(query)
        except ValueError:
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                internal_message=f"The provided query is invalid: {query}. Please refer to the Google Ads API documentation for the correct syntax: https://developers.google.com/google-ads/api/fields/v20/overview and test validate your query using the Google Ads Query Builder: https://developers.google.com/google-ads/api/fields/v20/query_validator",
                message=f"The provided query is invalid: {query}. Please refer to the Google Ads API documentation for the correct syntax: https://developers.google.com/google-ads/api/fields/v20/overview and test validate your query using the Google Ads Query Builder: https://developers.google.com/google-ads/api/fields/v20/query_validator",
            )


@dataclass
class StringParseState:
    inside_string: bool = False
    escape_next_character: bool = False
    collected_string_chars: List[str] = field(default_factory=list)
    last_parsed_key: Optional[str] = None


@dataclass
class TopLevelObjectState:
    depth: int = 0


@dataclass
class ResultsArrayState:
    inside_results_array: bool = False
    array_nesting_depth: int = 0
    expecting_results_array_start: bool = False


@dataclass
class RecordParseState:
    inside_record: bool = False
    record_text_buffer: List[str] = field(default_factory=list)
    record_nesting_depth: int = 0


@dataclass
class GoogleAdsStreamingDecoder(Decoder):
    """
    JSON streaming decoder optimized for Google Ads API responses.

    Uses a fast JSON parse when the full payload fits within max_direct_decode_bytes;
    otherwise streams records incrementally from the `results` array.
    Ensures truncated or structurally invalid JSON is detected and reported.
    """

    chunk_size: int = 5 * 1024 * 1024  # 5 MB
    # Fast-path threshold: if whole body < 20 MB, decode with json.loads
    max_direct_decode_bytes: int = 20 * 1024 * 1024  # 20 MB

    def __post_init__(self):
        self.parser = JsonParser()

    def is_stream_response(self) -> bool:
        return True

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        data, complete = self._buffer_up_to_limit(response)
        if complete:
            yield from self.parser.parse(io.BytesIO(data))
            return

        records_batch: List[Dict[str, Any]] = []
        for record in self._parse_records_from_stream(data):
            records_batch.append(record)
            if len(records_batch) >= 100:
                yield {"results": records_batch}
                records_batch = []

        if records_batch:
            yield {"results": records_batch}

    def _buffer_up_to_limit(self, response: requests.Response) -> Tuple[Union[bytes, Iterable[bytes]], bool]:
        buf = bytearray()
        response_stream = response.iter_content(chunk_size=self.chunk_size)

        while chunk := next(response_stream, None):
            buf.extend(chunk)
            if len(buf) >= self.max_direct_decode_bytes:
                return (self._chain_prefix_and_stream(bytes(buf), response_stream), False)
        return (bytes(buf), True)

    @staticmethod
    def _chain_prefix_and_stream(prefix: bytes, rest_stream: Iterable[bytes]) -> Iterable[bytes]:
        yield prefix
        yield from rest_stream

    def _parse_records_from_stream(self, byte_iter: Iterable[bytes], encoding: str = "utf-8") -> Generator[Dict[str, Any], None, None]:
        string_state = StringParseState()
        results_state = ResultsArrayState()
        record_state = RecordParseState()
        top_level_state = TopLevelObjectState()

        for chunk in byte_iter:
            for char in chunk.decode(encoding, errors="replace"):
                self._append_to_current_record_if_any(char, record_state)

                if self._update_string_state(char, string_state):
                    continue

                # Track outer braces only outside results array
                if not results_state.inside_results_array:
                    if char == "{":
                        top_level_state.depth += 1
                    elif char == "}":
                        top_level_state.depth = max(0, top_level_state.depth - 1)

                if not results_state.inside_results_array:
                    self._detect_results_array(char, string_state, results_state)
                    continue

                record = self._parse_record_structure(char, results_state, record_state)
                if record is not None:
                    yield record

        # EOF validation
        if (
            string_state.inside_string
            or record_state.inside_record
            or record_state.record_nesting_depth != 0
            or results_state.inside_results_array
            or results_state.array_nesting_depth != 0
            or top_level_state.depth != 0
        ):
            raise AirbyteTracedException(
                message="Response JSON stream ended prematurely and is incomplete.",
                internal_message=(
                    "Detected truncated JSON stream: one or more structural elements were not fully closed before the response ended."
                ),
                failure_type=FailureType.system_error,
            )

    def _update_string_state(self, char: str, state: StringParseState) -> bool:
        """Return True if char was handled as part of string parsing."""
        if state.inside_string:
            if state.escape_next_character:
                state.escape_next_character = False
                return True
            if char == "\\":
                state.escape_next_character = True
                return True
            if char == '"':
                state.inside_string = False
                state.last_parsed_key = "".join(state.collected_string_chars)
                state.collected_string_chars.clear()
                return True
            state.collected_string_chars.append(char)
            return True

        if char == '"':
            state.inside_string = True
            state.collected_string_chars.clear()
            return True

        return False

    def _detect_results_array(self, char: str, string_state: StringParseState, results_state: ResultsArrayState) -> None:
        if char == ":" and string_state.last_parsed_key == "results":
            results_state.expecting_results_array_start = True
        elif char == "[" and results_state.expecting_results_array_start:
            results_state.inside_results_array = True
            results_state.array_nesting_depth = 1
            results_state.expecting_results_array_start = False

    def _parse_record_structure(
        self, char: str, results_state: ResultsArrayState, record_state: RecordParseState
    ) -> Optional[Dict[str, Any]]:
        if char == "{":
            if record_state.inside_record:
                record_state.record_nesting_depth += 1
            else:
                self._start_record(record_state)
            return None

        if char == "}":
            if record_state.inside_record:
                record_state.record_nesting_depth -= 1
                if record_state.record_nesting_depth == 0:
                    return self._finish_record(record_state)
            return None

        if char == "[":
            if record_state.inside_record:
                record_state.record_nesting_depth += 1
            else:
                results_state.array_nesting_depth += 1
            return None

        if char == "]":
            if record_state.inside_record:
                record_state.record_nesting_depth -= 1
            else:
                results_state.array_nesting_depth -= 1
                if results_state.array_nesting_depth == 0:
                    results_state.inside_results_array = False

        return None

    @staticmethod
    def _append_to_current_record_if_any(char: str, record_state: RecordParseState):
        if record_state.inside_record:
            record_state.record_text_buffer.append(char)

    @staticmethod
    def _start_record(record_state: RecordParseState):
        record_state.inside_record = True
        record_state.record_text_buffer = ["{"]
        record_state.record_nesting_depth = 1

    @staticmethod
    def _finish_record(record_state: RecordParseState) -> Optional[Dict[str, Any]]:
        text = "".join(record_state.record_text_buffer).strip()
        record_state.inside_record = False
        record_state.record_text_buffer.clear()
        record_state.record_nesting_depth = 0
        return json.loads(text) if text else None
