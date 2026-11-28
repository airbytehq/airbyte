#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from unittest.mock import Mock, patch

from destination_opengauss_datavec.config import OpenGaussDataVecIndexingModel, PasswordBasedAuthorizationModel
from destination_opengauss_datavec.indexer import COPY_NULL_VALUE, OpenGaussDataVecIndexer, copy_value, rows_to_csv
from destination_opengauss_datavec.row_builder import (
    RowBuilder,
    chunk_id,
    document_id_for_chunk,
    embedding_value,
    metadata_value,
    record_emitted_at,
)
from destination_opengauss_datavec.schema import MetadataColumn, SchemaBuilder, normalize_identifier, schema_to_sql_type
from psycopg2.extras import Json

from airbyte_cdk.destinations.vector_db_based.config import ProcessingConfigModel
from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, Chunk
from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode


class FakeCursor:
    def __init__(self):
        self.executed = []
        self.copies = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def copy_expert(self, query, file):
        self.copies.append((query, file.getvalue()))


class FakeConnection:
    closed = 0

    def __init__(self):
        self.cursor_instance = FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def close(self):
        pass

    def commit(self):
        pass

    def cursor(self):
        return self.cursor_instance


def indexing_config():
    return OpenGaussDataVecIndexingModel(
        host="localhost",
        port=5432,
        database="db",
        default_schema="public",
        username="user",
        ssl_mode={"mode": "disable"},
        credentials=PasswordBasedAuthorizationModel(password="password"),
    )


def processing_config(metadata_fields=None, field_name_mappings=None):
    return ProcessingConfigModel(
        chunk_size=1000,
        metadata_fields=metadata_fields or [],
        field_name_mappings=field_name_mappings or [],
    )


def create_indexer(metadata_fields=None, field_name_mappings=None, omit_raw_text=False):
    return OpenGaussDataVecIndexer(
        indexing_config(),
        embedding_dimensions=3,
        processing_config=processing_config(metadata_fields, field_name_mappings),
        omit_raw_text=omit_raw_text,
    )


def configured_catalog():
    return ConfiguredAirbyteCatalog.parse_obj(
        {
            "streams": [
                {
                    "stream": {
                        "name": "Users",
                        "namespace": "ns1",
                        "json_schema": {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "category": {"type": "string"},
                                "source_id": {"type": "integer"},
                                "flag": {"type": "boolean"},
                                "score": {"type": "number"},
                                "created_at": {"type": "string", "format": "date-time"},
                                "nested": {"type": "object", "properties": {"value": {"type": "integer"}}},
                            },
                        },
                        "supported_sync_modes": ["full_refresh", "incremental"],
                    },
                    "primary_key": [["id"]],
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append_dedup",
                },
                {
                    "stream": {
                        "name": "This Is A Very Long Stream Name Designed To Exceed Sixty Two Characters For Truncation",
                        "json_schema": {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {"id": {"type": "integer"}, "title": {"type": "string"}},
                        },
                        "supported_sync_modes": ["full_refresh"],
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                },
            ]
        }
    )


def test_schema_builder_creates_destination_and_metadata_columns():
    builder = SchemaBuilder(
        processing_config(
            metadata_fields=["id", "source_id", "nested.value", "document_id", "missing_field"],
            field_name_mappings=[{"from_field": "source_id", "to_field": "sourceId"}],
        ),
        default_schema="public",
    )

    destination = builder.create_stream_destination(configured_catalog().streams[0])

    assert destination.schema_name == "ns1"
    assert destination.table_name == "Users"
    assert destination.write_table_name == "Users"
    assert destination.mode == DestinationSyncMode.append_dedup
    assert [(column.metadata_key, column.column_name, column.sql_type) for column in destination.metadata_columns] == [
        ("id", "id", "bigint"),
        ("sourceId", "sourceId", "bigint"),
        ("nested.value", "nested_value", "bigint"),
    ]

    default_schema_destination = builder.create_stream_destination(configured_catalog().streams[1])
    assert default_schema_destination.schema_name == "public"


def test_schema_builder_uses_top_level_fields_when_metadata_fields_are_empty_and_avoids_base_column_conflicts():
    catalog = ConfiguredAirbyteCatalog.parse_obj(
        {
            "streams": [
                {
                    "stream": {
                        "name": "events",
                        "json_schema": {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "document_id": {"type": "string"},
                                "content": {"type": "string"},
                                "payload": {"type": "object"},
                            },
                        },
                        "supported_sync_modes": ["full_refresh"],
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    destination = SchemaBuilder(processing_config(), default_schema="123 bad schema").create_stream_destination(catalog.streams[0])

    assert destination.schema_name == "_123_bad_schema"
    assert [(column.metadata_key, column.column_name, column.sql_type) for column in destination.metadata_columns] == [
        ("document_id", "_document_id", "text"),
        ("content", "_content", "text"),
        ("payload", "payload", "jsonb"),
    ]


def test_normalize_identifier_truncates_long_stream_name():
    name = normalize_identifier("This Is A Very Long Stream Name Designed To Exceed Sixty Two Characters For Truncation")

    assert len(name) <= 62
    assert name.startswith("This_Is_A_Very_Long_Stream_Name")
    assert name.rsplit("_", 1)[-1]


def test_schema_to_sql_type_uses_layered_fallback():
    assert schema_to_sql_type({"type": "string", "airbyte_type": "timestamp_without_timezone"}) == "timestamp"
    assert schema_to_sql_type({"type": "string", "format": "date"}) == "date"
    assert schema_to_sql_type({"type": "string"}) == "text"
    assert schema_to_sql_type({"type": "number"}) == "decimal"
    assert schema_to_sql_type({"type": "object"}) == "jsonb"
    assert schema_to_sql_type({}) == "jsonb"


def test_row_builder_omits_content_and_records_bigint_errors():
    builder = RowBuilder(omit_raw_text=True)
    columns = [
        MetadataColumn("category", "category", "text"),
        MetadataColumn("big_number", "big_number", "bigint"),
    ]
    record = AirbyteRecordMessage(stream="Users", namespace="ns1", emitted_at=1_700_000_000_000, data={"id": 1})
    chunk = Chunk(
        page_content=None,
        metadata={METADATA_RECORD_ID_FIELD: "ns1_Users_1", "category": "docs", "big_number": 9223372036854775808},
        record=record,
        embedding=[1, 2, 3],
    )

    assert builder.copy_columns(columns) == [
        "document_id",
        "chunk_id",
        "embedding",
        "category",
        "big_number",
        "_airbyte_extracted_at",
        "_airbyte_meta",
    ]
    row = list(builder.create_rows([chunk], columns))[0]

    assert row[0] == "ns1_Users_1"
    assert row[1] == "ns1_Users_1_0000_00000000"
    assert row[2] == "[1,2,3]"
    assert row[3] == "docs"
    assert row[4] is None
    assert isinstance(row[-1], Json)
    assert row[-1].adapted == {"changes": [{"field": "big_number", "change": "NULLED", "reason": "BIGINT_OVERFLOW"}]}


def test_row_builder_includes_content_json_metadata_and_emitted_at():
    builder = RowBuilder(omit_raw_text=False)
    columns = [
        MetadataColumn("payload", "payload", "jsonb"),
        MetadataColumn("tags", "tags", "jsonb"),
        MetadataColumn("nested", "nested", "text"),
    ]
    record = AirbyteRecordMessage(stream="Users", namespace="ns1", emitted_at=1_700_000_000_000, data={"id": 1})
    chunk = Chunk(
        page_content="hello",
        metadata={
            METADATA_RECORD_ID_FIELD: "ns1_Users_1",
            "payload": {"k": "v"},
            "tags": ["a", "b"],
            "nested": {"value": 1},
        },
        record=record,
        embedding=[1, 2, 3],
    )

    assert builder.copy_columns(columns) == [
        "document_id",
        "chunk_id",
        "content",
        "embedding",
        "payload",
        "tags",
        "nested",
        "_airbyte_extracted_at",
        "_airbyte_meta",
    ]
    row = list(builder.create_rows([chunk], columns))[0]

    assert row[0] == "ns1_Users_1"
    assert row[2] == "hello"
    assert row[4].adapted == {"k": "v"}
    assert row[5].adapted == ["a", "b"]
    assert row[6] == '{"value": 1}'
    assert row[7] == datetime.fromtimestamp(1_700_000_000_000 / 1000, timezone.utc)
    assert row[8].adapted == {"changes": []}


def test_metadata_value_distinguishes_int_conversion_and_overflow():
    column = MetadataColumn("value", "value", "bigint")

    assert metadata_value("123", column) == (123, None)
    assert metadata_value("not-int", column)[1]["reason"] == "INT_CONVERSION_FAILED: Expected bigint value, but got not-int"
    assert metadata_value(9223372036854775808, column)[1]["reason"] == "BIGINT_OVERFLOW"


def test_metadata_value_coerces_boolean_values():
    column = MetadataColumn("flag", "flag", "boolean")

    assert metadata_value(True, column) == (True, None)
    assert metadata_value("false", column) == (False, None)
    assert metadata_value(1, column) == (True, None)
    assert metadata_value("not-bool", column)[1]["reason"] == "BOOLEAN_CONVERSION_FAILED: Expected boolean value, but got not-bool"


def test_metadata_value_serializes_jsonb_and_plain_nested_values():
    jsonb_column = MetadataColumn("payload", "payload", "jsonb")
    text_column = MetadataColumn("payload", "payload", "text")

    jsonb_value, jsonb_change = metadata_value({"nested": True}, jsonb_column)
    text_value, text_change = metadata_value(["a", "b"], text_column)

    assert jsonb_value.adapted == {"nested": True}
    assert jsonb_change is None
    assert text_value == '["a", "b"]'
    assert text_change is None


def test_chunk_id_and_embedding_serialization():
    assert chunk_id("doc", 3, None) == "doc_0003_00000000"
    assert chunk_id("doc", 3, "hello").startswith("doc_0003_")
    assert embedding_value([1.0, 2.5, -3]) == "[1.0,2.5,-3]"


def test_embedding_value_rejects_missing_embeddings():
    try:
        embedding_value(None)
        assert False, "Expected embedding_value to reject missing embeddings"
    except ValueError as exc:
        assert "without an embedding" in str(exc)


def test_document_id_for_chunk_reuses_generated_id_for_chunks_from_same_record():
    record = AirbyteRecordMessage(stream="Users", namespace="ns1", emitted_at=1_700_000_000_000, data={"id": 1})
    generated_document_ids = {}
    first_chunk = Chunk(page_content="a", metadata={}, record=record, embedding=[1, 2, 3])
    second_chunk = Chunk(page_content="b", metadata={}, record=record, embedding=[1, 2, 3])

    with patch("destination_opengauss_datavec.row_builder.uuid.uuid4", return_value="generated"):
        first_id = document_id_for_chunk(first_chunk, generated_document_ids)
        second_id = document_id_for_chunk(second_chunk, generated_document_ids)

    assert first_id == "ns1_Users_generated"
    assert second_id == first_id


def test_record_emitted_at_returns_none_when_record_has_no_timestamp():
    record = Mock(stream="Users", namespace="ns1", emitted_at=None)
    chunk = Chunk(page_content="a", metadata={}, record=record, embedding=[1, 2, 3])

    assert record_emitted_at(chunk) is None


def test_pre_sync_creates_tables_and_indexes():
    indexer = create_indexer(metadata_fields=["id", "category"])
    connection = FakeConnection()

    with patch("destination_opengauss_datavec.indexer.get_connection", return_value=connection):
        indexer.pre_sync(configured_catalog())

    assert "ns1_Users" in indexer.streams
    assert indexer.streams["ns1_Users"].table_name == "Users"
    assert indexer.streams["ns1_Users"].metadata_columns[0].column_name == "id"
    assert len(connection.cursor_instance.executed) >= 5


def test_index_uses_copy_with_rows():
    indexer = create_indexer(metadata_fields=["category"])
    connection = FakeConnection()
    with (
        patch("destination_opengauss_datavec.indexer.get_connection", return_value=connection),
        patch("psycopg2.sql.Composed.as_string", return_value="COPY statement"),
    ):
        indexer.pre_sync(configured_catalog())

        record = AirbyteRecordMessage(stream="Users", namespace="ns1", emitted_at=1_700_000_000_000, data={"id": 1})
        chunk = Chunk(
            page_content="hello",
            metadata={METADATA_RECORD_ID_FIELD: "ns1_Users_1", "category": "docs"},
            record=record,
            embedding=[1, 2, 3],
        )

        indexer.index([chunk], "ns1", "Users")

    assert len(connection.cursor_instance.copies) == 1
    assert connection.cursor_instance.copies[0][1].startswith("ns1_Users_1,")


def test_index_returns_without_database_call_for_empty_batch():
    indexer = create_indexer(metadata_fields=["category"])

    with patch("destination_opengauss_datavec.indexer.get_connection") as get_connection:
        indexer.index([], "ns1", "Users")

    get_connection.assert_not_called()


def test_delete_only_runs_for_append_dedup():
    indexer = create_indexer(metadata_fields=["category"])
    connection = FakeConnection()
    with patch("destination_opengauss_datavec.indexer.get_connection", return_value=connection):
        indexer.pre_sync(configured_catalog())

        indexer.delete(["ns1_Users_1"], "ns1", "Users")

    assert connection.cursor_instance.executed[-1][1] == (["ns1_Users_1"],)


def test_delete_returns_without_database_call_for_empty_ids():
    indexer = create_indexer(metadata_fields=["category"])

    with patch("destination_opengauss_datavec.indexer.get_connection") as get_connection:
        indexer.delete([], "ns1", "Users")

    get_connection.assert_not_called()


def test_delete_skips_non_append_dedup_streams():
    indexer = create_indexer(metadata_fields=["category"])
    connection = FakeConnection()
    with patch("destination_opengauss_datavec.indexer.get_connection", return_value=connection):
        indexer.pre_sync(configured_catalog())
        executed_before_delete = len(connection.cursor_instance.executed)

        indexer.delete(["doc"], None, configured_catalog().streams[1].stream.name)

    assert len(connection.cursor_instance.executed) == executed_before_delete


def test_post_sync_promotes_overwrite_tables_and_returns_empty_state_messages():
    indexer = create_indexer(metadata_fields=["title"])
    connection = FakeConnection()
    with patch("destination_opengauss_datavec.indexer.get_connection", return_value=connection):
        indexer.pre_sync(configured_catalog())
        executed_before_post_sync = len(connection.cursor_instance.executed)

        result = indexer.post_sync()

    assert result == []
    assert len(connection.cursor_instance.executed) == executed_before_post_sync + 2


def test_post_sync_returns_empty_list_without_database_call_when_no_overwrite_streams():
    indexer = create_indexer(metadata_fields=["category"])
    indexer.streams = {"ns1_Users": indexer.schema_builder.create_stream_destination(configured_catalog().streams[0])}

    with patch("destination_opengauss_datavec.indexer.get_connection") as get_connection:
        result = indexer.post_sync()

    assert result == []
    get_connection.assert_not_called()


def test_check_returns_none_on_success_and_error_message_on_failure():
    success_connection = FakeConnection()
    indexer = create_indexer()

    with patch("destination_opengauss_datavec.indexer.get_connection", return_value=success_connection):
        assert indexer.check() is None

    with patch("destination_opengauss_datavec.indexer.get_connection", side_effect=Exception("connection failed")):
        assert "connection failed" in indexer.check()


def test_rows_to_csv_serializes_nulls_and_json_values_for_copy():
    csv_file = rows_to_csv([("doc", None, Json({"k": "v"}), True)])

    assert csv_file.getvalue() == f'doc,{COPY_NULL_VALUE},"{{""k"": ""v""}}",True\r\n'


def test_copy_value_handles_null_json_and_plain_values():
    assert copy_value(None) == COPY_NULL_VALUE
    assert copy_value(Json(["a"])) == '["a"]'
    assert copy_value("plain") == "plain"
