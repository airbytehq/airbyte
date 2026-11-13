#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from contextlib import closing, contextmanager
from decimal import Decimal
from typing import Any, Optional

import psycopg2
import pytest
from destination_opengauss_datavec.destination import DestinationOpenGaussDataVec
from destination_opengauss_datavec.schema import normalize_identifier
from psycopg2 import sql

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


NAMESPACE_STREAM_NAME = "integration_namespace_docs"
FIRST_NAMESPACE = "integration_namespace_one"
SECOND_NAMESPACE = "integration_namespace_two"


class TestOpenGaussDataVecIntegration:
    @pytest.fixture(autouse=True)
    def setup_config(self, opengauss_config):
        self.config = opengauss_config
        self.schema = self.config["indexing"]["default_schema"]

    def teardown_method(self):
        default_schema_tables = [
            "integration_overwrite_articles",
            "integration_append_events",
            "integration_dedup_docs",
            "integration_type_mapping",
            "integration_all_type_mapping",
            "integration_omit_raw_text",
            "integration_append_schema_evolution",
            "integration_field_mapping",
            normalize_identifier("integration_long_stream_name_" + "x" * 80),
        ]
        namespace_schemas = [FIRST_NAMESPACE, SECOND_NAMESPACE]

        for table_name in default_schema_tables:
            self._drop_table(table_name)
            self._drop_table(normalize_identifier(f"_airbyte_tmp_{table_name}"))
        for schema in namespace_schemas:
            self._drop_schema(schema)

    def test_check_valid_config(self):
        outcome = DestinationOpenGaussDataVec().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config(self):
        bad_config = {
            **self.config,
            "indexing": {
                **self.config["indexing"],
                "host": "invalid-host",
                "connect_timeout": 1,
            },
        }
        outcome = DestinationOpenGaussDataVec().check(logging.getLogger("airbyte"), bad_config)
        assert outcome.status == Status.FAILED

    def test_write_overwrite_append_and_append_dedup(self):
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                self._configured_stream("integration_overwrite_articles", DestinationSyncMode.overwrite),
                self._configured_stream("integration_append_events", DestinationSyncMode.append),
                self._configured_stream("integration_dedup_docs", DestinationSyncMode.append_dedup),
            ]
        )
        destination = DestinationOpenGaussDataVec()

        first_messages = [
            self._record("integration_overwrite_articles", 1, "overwrite first"),
            self._record("integration_append_events", 10, "append first"),
            self._record("integration_dedup_docs", 100, "dedup first"),
            self._state("first"),
        ]
        list(destination.write(self.config, catalog, first_messages))

        assert self._count("integration_overwrite_articles") == 1
        assert self._count("integration_append_events") == 1
        assert self._count("integration_dedup_docs") == 1

        second_messages = [
            self._record("integration_overwrite_articles", 2, "overwrite replacement"),
            self._record("integration_append_events", 11, "append second"),
            self._record("integration_dedup_docs", 100, "dedup replacement"),
            self._state("second"),
        ]
        list(destination.write(self.config, catalog, second_messages))

        assert self._count("integration_overwrite_articles") == 1
        assert self._count("integration_append_events") == 2
        assert self._count("integration_dedup_docs") == 1
        assert self._contents("integration_overwrite_articles") == ["title: overwrite replacement"]
        assert sorted(self._contents("integration_append_events")) == ["title: append first", "title: append second"]
        assert self._contents("integration_dedup_docs") == ["title: dedup replacement"]

    def test_write_type_mapping_and_bigint_meta_changes(self):
        config = {
            **self.config,
            "processing": {
                **self.config["processing"],
                "metadata_fields": [
                    "id",
                    "title",
                    "category",
                    "flag",
                    "score",
                    "created_at",
                    "event_date",
                    "source_id",
                    "big_number",
                ],
            },
        }
        catalog = ConfiguredAirbyteCatalog(
            streams=[self._configured_stream("integration_type_mapping", DestinationSyncMode.append_dedup, type_schema=True)]
        )
        messages = [
            self._typed_record(1, "normal", 9223372036854775807),
            self._typed_record(2, "overflow", 9223372036854775808),
            self._typed_record(3, "conversion", "not-an-int"),
            self._state("types"),
        ]

        list(DestinationOpenGaussDataVec().write(config, catalog, messages))

        assert self._count("integration_type_mapping") == 3
        changes = self._meta_changes("integration_type_mapping")
        assert any(change["reason"] == "BIGINT_OVERFLOW" for row in changes for change in row)
        assert any(change["reason"].startswith("INT_CONVERSION_FAILED") for row in changes for change in row)

    def test_write_all_type_mappings(self):
        config = self._config_with_metadata_fields(
            [
                "id",
                "title",
                "flag",
                "score",
                "created_at",
                "event_date",
                "source_id",
                "tags",
                "attributes",
                "decimal_amount",
                "float_amount",
                "airbyte_created_at",
                "created_without_tz",
                "time_with_tz",
                "time_without_tz",
                "big_integer_amount",
            ]
        )
        extra_properties = {
            "flag": {"type": "boolean"},
            "score": {"type": "number"},
            "created_at": {"type": "string", "format": "date-time"},
            "event_date": {"type": "string", "format": "date"},
            "source_id": {"type": "integer"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "attributes": {"type": "object"},
            "decimal_amount": {"type": "number", "airbyte_type": "decimal"},
            "float_amount": {"type": "number", "airbyte_type": "float"},
            "airbyte_created_at": {"type": "string", "airbyte_type": "timestamp_with_timezone"},
            "created_without_tz": {"type": "string", "airbyte_type": "timestamp_without_timezone"},
            "time_with_tz": {"type": "string", "airbyte_type": "time_with_timezone"},
            "time_without_tz": {"type": "string", "airbyte_type": "time_without_timezone"},
            "big_integer_amount": {"type": "integer", "airbyte_type": "big_integer"},
        }
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                self._configured_stream(
                    "integration_all_type_mapping",
                    DestinationSyncMode.overwrite,
                    extra_properties=extra_properties,
                )
            ]
        )
        messages = [
            self._data_record(
                "integration_all_type_mapping",
                {
                    "id": 1,
                    "title": "all types",
                    "flag": True,
                    "score": 12.34,
                    "created_at": "2024-01-02T03:04:05Z",
                    "event_date": "2024-01-02",
                    "source_id": 42,
                    "tags": ["one", "two"],
                    "attributes": {"source": "integration"},
                    "decimal_amount": "123.45",
                    "float_amount": 67.89,
                    "airbyte_created_at": "2024-01-02T03:04:05Z",
                    "created_without_tz": "2024-01-02 03:04:05",
                    "time_with_tz": "03:04:05+00",
                    "time_without_tz": "03:04:05",
                    "big_integer_amount": 9223372036854775807,
                },
            ),
            self._state("all-types"),
        ]

        list(DestinationOpenGaussDataVec().write(config, catalog, messages))

        column_types = self._column_types("integration_all_type_mapping")
        assert column_types["flag"] == "boolean"
        assert column_types["score"] in ("decimal", "numeric")
        assert column_types["created_at"] == "timestamp with time zone"
        assert column_types["event_date"] in ("date", "timestamp without time zone")
        assert column_types["source_id"] == "bigint"
        assert column_types["title"] == "text"
        assert column_types["tags"] == "jsonb"
        assert column_types["attributes"] == "jsonb"
        assert column_types["decimal_amount"] in ("decimal", "numeric")
        assert column_types["float_amount"] in ("decimal", "numeric")
        assert column_types["airbyte_created_at"] == "timestamp with time zone"
        assert column_types["created_without_tz"] == "timestamp without time zone"
        assert column_types["time_with_tz"] == "time with time zone"
        assert column_types["time_without_tz"] == "time without time zone"
        assert column_types["big_integer_amount"] == "bigint"
        values = self._row_values(
            "integration_all_type_mapping",
            ["flag", "score", "event_date", "source_id", "tags", "attributes", "decimal_amount", "float_amount"],
        )
        assert values == [True, 12.34, "2024-01-02", 42, ["one", "two"], {"source": "integration"}, 123.45, 67.89]

    def test_write_omit_raw_text(self):
        config = {**self.config, "omit_raw_text": True}
        catalog = ConfiguredAirbyteCatalog(streams=[self._configured_stream("integration_omit_raw_text", DestinationSyncMode.overwrite)])
        messages = [self._record("integration_omit_raw_text", 1, "without raw text"), self._state("omit")]

        list(DestinationOpenGaussDataVec().write(config, catalog, messages))

        assert self._count("integration_omit_raw_text") == 1
        assert "content" not in self._column_types("integration_omit_raw_text")

    def test_write_append_adds_new_metadata_column(self):
        stream_name = "integration_append_schema_evolution"
        catalog = ConfiguredAirbyteCatalog(streams=[self._configured_stream(stream_name, DestinationSyncMode.append)])
        list(DestinationOpenGaussDataVec().write(self.config, catalog, [self._record(stream_name, 1, "first"), self._state("first")]))

        config = self._config_with_metadata_fields(["id", "title", "category", "new_field"])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                self._configured_stream(
                    stream_name,
                    DestinationSyncMode.append,
                    extra_properties={"new_field": {"type": "string"}},
                )
            ]
        )
        list(
            DestinationOpenGaussDataVec().write(
                config,
                catalog,
                [
                    self._data_record(
                        stream_name,
                        {"id": 2, "title": "second", "category": "integration", "new_field": "new value"},
                    ),
                    self._state("second"),
                ],
            )
        )

        assert self._count(stream_name) == 2
        assert self._column_types(stream_name)["new_field"] == "text"
        assert self._row_values(stream_name, ["new_field"], where='"id" = 2') == ["new value"]

    def test_write_field_name_mappings(self):
        config = self._config_with_metadata_fields(["source_id"])
        config["processing"]["field_name_mappings"] = [{"from_field": "source_id", "to_field": "sourceId"}]
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                self._configured_stream(
                    "integration_field_mapping",
                    DestinationSyncMode.overwrite,
                    extra_properties={"source_id": {"type": "integer"}},
                )
            ]
        )
        messages = [
            self._data_record(
                "integration_field_mapping",
                {"id": 1, "title": "mapped", "category": "integration", "source_id": 99},
            ),
            self._state("mapping"),
        ]

        list(DestinationOpenGaussDataVec().write(config, catalog, messages))

        assert self._column_types("integration_field_mapping")["sourceId"] == "bigint"
        assert self._row_values("integration_field_mapping", ["sourceId"]) == [99]

    def test_write_long_stream_name(self):
        stream_name = "integration_long_stream_name_" + "x" * 80
        catalog = ConfiguredAirbyteCatalog(streams=[self._configured_stream(stream_name, DestinationSyncMode.overwrite)])
        messages = [self._record(stream_name, 1, "long stream"), self._state("long")]

        list(DestinationOpenGaussDataVec().write(self.config, catalog, messages))

        assert self._count(normalize_identifier(stream_name)) == 1

    def test_write_same_stream_name_different_namespaces(self):
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                self._configured_stream(NAMESPACE_STREAM_NAME, DestinationSyncMode.overwrite, namespace=FIRST_NAMESPACE),
                self._configured_stream(NAMESPACE_STREAM_NAME, DestinationSyncMode.overwrite, namespace=SECOND_NAMESPACE),
            ]
        )
        messages = [
            self._record(NAMESPACE_STREAM_NAME, 1, "namespace one", namespace=FIRST_NAMESPACE),
            self._record(NAMESPACE_STREAM_NAME, 2, "namespace two", namespace=SECOND_NAMESPACE),
            self._state("namespaces"),
        ]

        list(DestinationOpenGaussDataVec().write(self.config, catalog, messages))

        assert self._count(NAMESPACE_STREAM_NAME, schema=FIRST_NAMESPACE) == 1
        assert self._count(NAMESPACE_STREAM_NAME, schema=SECOND_NAMESPACE) == 1
        assert self._contents(NAMESPACE_STREAM_NAME, schema=FIRST_NAMESPACE) == ["title: namespace one"]
        assert self._contents(NAMESPACE_STREAM_NAME, schema=SECOND_NAMESPACE) == ["title: namespace two"]

    def _configured_stream(
        self,
        name: str,
        mode: DestinationSyncMode,
        type_schema: bool = False,
        namespace: Optional[str] = None,
        extra_properties: Optional[dict] = None,
    ) -> ConfiguredAirbyteStream:
        properties = {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "category": {"type": "string"},
        }
        if type_schema:
            properties.update(
                {
                    "flag": {"type": "boolean"},
                    "score": {"type": "number"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "event_date": {"type": "string", "format": "date"},
                    "source_id": {"type": "integer"},
                    "big_number": {"type": "integer"},
                }
            )
        if extra_properties:
            properties.update(extra_properties)

        return ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name=name,
                namespace=namespace,
                json_schema={"type": "object", "properties": properties},
                supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
            ),
            primary_key=[["id"]],
            sync_mode=SyncMode.incremental,
            destination_sync_mode=mode,
        )

    def _record(self, stream: str, record_id: int, title: str, namespace: Optional[str] = None) -> AirbyteMessage:
        return self._data_record(stream, {"id": record_id, "title": title, "category": "integration"}, namespace)

    def _data_record(self, stream: str, data: dict, namespace: Optional[str] = None) -> AirbyteMessage:
        return AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=stream,
                namespace=namespace,
                data=data,
                emitted_at=1_700_000_000_000,
            ),
        )

    def _typed_record(self, record_id: int, title: str, big_number) -> AirbyteMessage:
        return AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="integration_type_mapping",
                data={
                    "id": record_id,
                    "title": title,
                    "category": "types",
                    "flag": True,
                    "score": 12.34,
                    "created_at": "2024-01-02T03:04:05Z",
                    "event_date": "2024-01-02",
                    "source_id": record_id,
                    "big_number": big_number,
                },
                emitted_at=1_700_000_000_000,
            ),
        )

    def _state(self, value: str) -> AirbyteMessage:
        return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": value}))

    def _config_with_metadata_fields(self, metadata_fields: list):
        return {
            **self.config,
            "processing": {
                **self.config["processing"],
                "metadata_fields": metadata_fields,
            },
        }

    @contextmanager
    def _connect(self):
        indexing = self.config["indexing"]
        ssl_mode = indexing.get("ssl_mode", {"mode": "disable"})
        with closing(
            psycopg2.connect(
                host=indexing["host"],
                port=indexing["port"],
                dbname=indexing["database"],
                user=indexing["username"],
                password=indexing["credentials"]["password"],
                sslmode=ssl_mode["mode"],
                connect_timeout=20,
            )
        ) as conn:
            with conn:
                yield conn

    def _drop_table(self, table_name: str, schema: Optional[str] = None):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'DROP TABLE IF EXISTS "{normalize_identifier(schema or self.schema)}"."{table_name}" CASCADE')

    def _drop_schema(self, schema: str):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'DROP SCHEMA IF EXISTS "{normalize_identifier(schema)}" CASCADE')

    def _count(self, table_name: str, schema: Optional[str] = None) -> int:
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'SELECT COUNT(*) FROM "{normalize_identifier(schema or self.schema)}"."{table_name}"')
                return cursor.fetchone()[0]

    def _contents(self, table_name: str, schema: Optional[str] = None):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'SELECT content FROM "{normalize_identifier(schema or self.schema)}"."{table_name}" ORDER BY document_id')
                return [row[0] for row in cursor.fetchall()]

    def _meta_changes(self, table_name: str):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'SELECT _airbyte_meta FROM "{self.schema}"."{table_name}" ORDER BY document_id')
                return [row[0]["changes"] for row in cursor.fetchall()]

    def _column_types(self, table_name: str):
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    """,
                    (self.schema, table_name),
                )
                return {row[0]: row[1] for row in cursor.fetchall()}

    def _row_values(self, table_name: str, columns: list, where: Optional[str] = None):
        query = sql.SQL("SELECT {} FROM {}.{}").format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(self.schema),
            sql.Identifier(table_name),
        )
        if where:
            query += sql.SQL(" WHERE ") + sql.SQL(where)
        query += sql.SQL(" ORDER BY document_id")

        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                return [self._normalized_value(value) for value in row]

    def _normalized_value(self, value: Any):
        if hasattr(value, "isoformat"):
            iso_value = value.isoformat()
            if iso_value == "2024-01-02T00:00:00":
                return "2024-01-02"
            return iso_value
        if isinstance(value, Decimal):
            return round(float(value), 2)
        if isinstance(value, float):
            return round(value, 2)
        return value
