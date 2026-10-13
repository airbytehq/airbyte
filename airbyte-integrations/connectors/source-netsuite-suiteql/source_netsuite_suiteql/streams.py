# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from importlib.resources import files
from typing import Any, Iterable, Mapping, MutableMapping, Sequence, TypedDict

import requests
from requests_oauthlib import OAuth1

from airbyte_cdk.sources.streams.http import HttpStream

from .errors import MissingCursorFieldError, raise_for_netsuite_status


SCHEMA_SAMPLE_SIZE = 100
CURSOR_ALIAS = "cursor_ts"
CURSOR_FORMAT = "YYYY-MM-DD HH24:MI:SS"
SchemaProperties = Mapping[str, Mapping[str, Any]]
SuiteQLJsonSchema = TypedDict(
    "SuiteQLJsonSchema",
    {
        "$schema": str,
        "type": str,
        "properties": SchemaProperties,
    },
)


class SchemaProcessor:
    json_types = {
        type(None): "null",
        bool: "boolean",
        int: "integer",
        float: "number",
        dict: "object",
        list: "array",
        str: "string",
    }

    def __init__(self) -> None:
        self._field_types: dict[str, set[str]] = {}

    @classmethod
    def infer(cls, records: Iterable[Mapping[str, Any]]) -> SchemaProperties:
        processor = cls()
        for record in records:
            processor.add(record)
        return processor.properties

    def add(self, record: Mapping[str, Any]) -> None:
        for field, value in record.items():
            types = self._field_types.setdefault(field, set())
            types.update(self._types_for(value))

    @property
    def properties(self) -> SchemaProperties:
        properties = {}
        for field, types in self._field_types.items():
            properties[field] = {"type": self._nullable_types(types)}
        return properties

    def _types_for(self, value: Any) -> set[str]:
        value_type = self.json_types.get(type(value), "string")
        return {"null", value_type}

    def _nullable_types(self, types: set[str]) -> list[str]:
        return ["null", *sorted(types - {"null"})]


class SuiteqlStream(HttpStream):
    api_path = "/services/rest/query/v1/suiteql"

    def __init__(
        self,
        table_name: str,
        base_url: str,
        page_size: int,
        auth: OAuth1,
        primary_key: Sequence[str] = (),
        cursor_field: str | None = None,
    ) -> None:
        self.table_name = table_name
        self._url_base = base_url
        self.page_size = page_size
        self._primary_key = [[field] for field in primary_key]
        self.source_cursor_field = cursor_field
        self._schema: Mapping[str, Any] | None = None
        super().__init__(authenticator=auth)

    @staticmethod
    def build_query(
        table_name: str,
        primary_key: Sequence[str],
        cursor_field: str | None,
        incremental: bool = False,
    ) -> str:
        query = f"SELECT * FROM {table_name}"

        if cursor_field:
            query = f"SELECT *, TO_CHAR({cursor_field}, '{CURSOR_FORMAT}') AS {CURSOR_ALIAS} FROM {table_name}"

        if incremental and cursor_field:
            query += f" WHERE {cursor_field} >= TO_DATE(?, '{CURSOR_FORMAT}')"

        order_by = ([CURSOR_ALIAS] if cursor_field else []) + list(primary_key)
        return f"{query} ORDER BY {', '.join(order_by)}" if order_by else query

    @property
    def name(self) -> str:
        return self.table_name

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    def http_method(self) -> str:
        return "POST"

    @property
    def cursor_field(self) -> str | list[str]:
        return self.source_cursor_field or []

    @property
    def primary_key(self) -> list[list[str]]:
        return self._primary_key

    @property
    def supports_incremental(self) -> bool:
        return True

    @property
    def is_resumable(self) -> bool:
        return self.source_cursor_field is not None

    def path(self, **kwargs) -> str:
        return self.api_path

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Prefer": "transient"}

    def request_params(
        self,
        stream_state: Mapping[str, Any] | None,  # needed by CDK
        stream_slice: Mapping[str, Any] | None = None,  # needed by CDK
        next_page_token: Mapping[str, Any] | None = None,
    ) -> MutableMapping[str, Any]:
        return dict(next_page_token or {"limit": self.page_size, "offset": 0})

    def request_body_json(self, stream_state: Mapping[str, Any] | None = None, **kwargs) -> Mapping[str, Any]:
        cursor = stream_state.get(self.cursor_field) if stream_state and self.source_cursor_field else None
        body: dict[str, Any] = {
            "q": self.build_query(
                self.table_name,
                [field[0] for field in self.primary_key],
                self.source_cursor_field,
                cursor is not None,
            )
        }
        if cursor is not None:
            body["params"] = [cursor]

        return body

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        cursor_field = self.cursor_field
        if not cursor_field:
            return current_stream_state

        latest_cursor = latest_record.get(cursor_field)
        if latest_cursor is None:
            raise MissingCursorFieldError(cursor_field)

        current_cursor = current_stream_state.get(cursor_field)
        return {cursor_field: max(cursor for cursor in (current_cursor, latest_cursor) if cursor is not None)}

    def next_page_token(self, response: requests.Response) -> Mapping[str, Any] | None:
        payload = response.json()

        if payload.get("hasMore"):
            return {"limit": self.page_size, "offset": payload["offset"] + payload["count"]}

        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping[str, Any]]:
        for item in response.json().get("items", []):
            record = dict(item)

            has_cursor = self.source_cursor_field and CURSOR_ALIAS in record
            if has_cursor:
                record[self.source_cursor_field] = record.pop(CURSOR_ALIAS)

            yield record

    def get_json_schema(self) -> Mapping[str, Any]:
        if self._schema is None:
            self._reset_schema()
        return self._schema

    def _reset_schema(self) -> None:
        response = self._session.post(
            self.url_base + self.api_path,
            headers=self.request_headers(),
            params={"limit": SCHEMA_SAMPLE_SIZE, "offset": 0},
            json=self.request_body_json(),
        )
        raise_for_netsuite_status(response)
        records = response.json().get("items", [])
        properties = dict(SchemaProcessor.infer(records))
        schema_hint = self._schema_hint()
        for field, field_schema in schema_hint.get("properties", {}).items():
            properties.setdefault(field, field_schema)

        schema: SuiteQLJsonSchema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }
        self._schema = schema

    def _schema_hint(self) -> Mapping[str, Any]:
        schema_path = files("source_netsuite_suiteql").joinpath("schemas", f"{self.table_name.lower()}.json")
        if not schema_path.is_file():
            return {}
        return json.loads(schema_path.read_text(encoding="utf-8"))
