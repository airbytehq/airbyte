# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
from contextlib import closing
from unittest.mock import Mock

import pyarrow as pa
import pytest
from source_redis_adbc.backend import AdbcBackend, ConnectorError, connect, quote, validate_config
from source_redis_adbc.conversion import schema_to_json
from source_redis_adbc.source import SourceRedisAdbc


CONFIG = {"uri": "redis://user:secret@localhost:6379/0"}
SCHEMA = pa.schema([pa.field("id", pa.int64()), pa.field("label", pa.string())])


class Reader:
    def __init__(self, batches, schema=SCHEMA, late_error=None):
        self.schema = schema
        self.batches = list(batches)
        self.late_error = late_error
        self.consumed = 0
        self.closed = False

    def __iter__(self):
        for batch in self.batches:
            self.consumed += 1
            yield batch
        if self.late_error:
            raise self.late_error

    def close(self):
        self.closed = True


def metadata(catalog="redis", namespace="public", name="items"):
    return {
        "catalog_name": catalog,
        "catalog_db_schemas": [{"db_schema_name": namespace, "db_schema_tables": [{"table_name": name, "table_type": "TABLE"}]}],
    }


def backend(reader, rows=None):
    connection = Mock()
    cursor = connection.cursor.return_value
    cursor.fetch_record_batch.return_value = reader
    connection.adbc_get_objects.side_effect = lambda **kw: Reader([pa.RecordBatch.from_pylist(rows or [metadata()])])
    connection.adbc_get_table_schema.return_value = SCHEMA
    factory = Mock(return_value=connection)
    return AdbcBackend(CONFIG, factory), connection, cursor


def selection(schema=SCHEMA):
    return [("public", "items", schema_to_json(schema)["properties"])]


def test_multibatch_is_lazy_and_closes():
    batches = [pa.record_batch([[n], [str(n)]], schema=SCHEMA) for n in range(3)]
    reader = Reader(batches)
    source, connection, cursor = backend(reader)
    gen = source.read(selection())
    assert next(gen)[1] == {"id": "0", "label": "0"}
    assert reader.consumed == 1  # backpressure: later batches are not requested
    assert [record for _, record in gen] == [{"id": "1", "label": "1"}, {"id": "2", "label": "2"}]
    assert reader.closed
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
    cursor.adbc_cancel.assert_not_called()


def test_early_consumer_cancellation_closes_and_cancels():
    reader = Reader([pa.record_batch([[1], ["a"]], schema=SCHEMA)])
    source, connection, cursor = backend(reader)
    with closing(source.read(selection())) as gen:
        next(gen)
    assert reader.closed
    cursor.adbc_cancel.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_late_error_sanitized_after_partial_output():
    reader = Reader([pa.record_batch([[1], ["a"]], schema=SCHEMA)], late_error=RuntimeError(CONFIG["uri"]))
    source, connection, cursor = backend(reader)
    gen = source.read(selection())
    next(gen)
    with pytest.raises(ConnectorError) as exc:
        next(gen)
    assert "secret" not in str(exc.value)
    assert exc.value.__suppress_context__
    assert reader.closed
    cursor.adbc_cancel.assert_called_once()
    connection.close.assert_called_once()


def test_check_consumes_late_error():
    reader = Reader([], late_error=RuntimeError("password=secret"))
    source, connection, cursor = backend(reader)
    with pytest.raises(ConnectorError):
        source.check()
    assert reader.closed
    connection.close.assert_called_once()


def test_empty_result_has_no_records_and_closes():
    reader = Reader([])
    source, connection, _ = backend(reader)
    assert list(source.read(selection())) == []
    assert reader.closed
    connection.close.assert_called_once()


def test_selected_field_and_quoted_identifiers():
    projected = pa.schema([SCHEMA.field("id")])
    reader = Reader([pa.record_batch([[1]], schema=projected)], schema=projected)
    source, _, cursor = backend(reader, [metadata(name='items"; DROP TABLE t;--')])
    selected = [("public", 'items"; DROP TABLE t;--', schema_to_json(projected)["properties"])]
    assert list(source.read(selected))[0][1] == {"id": "1"}
    cursor.execute.assert_called_once_with('SELECT "id" FROM "redis"."public"."items""; DROP TABLE t;--"')
    assert quote('a"b') == '"a""b"'


@pytest.mark.parametrize(
    "selections",
    [
        [("public", "missing", {"id": {"type": "string"}})],
        [("public", "items", {"gone": {"type": "string"}})],
        [("public", "items", {"id": {"type": "integer"}})],
        [("public", "items", {})],
        selection() * 2,
    ],
)
def test_invalid_selection_fails_before_query(selections):
    source, connection, cursor = backend(Reader([]))
    with pytest.raises(ConnectorError):
        list(source.read(selections))
    cursor.execute.assert_not_called()
    connection.close.assert_called_once()


def test_ambiguous_catalog_fails():
    source, _, _ = backend(Reader([]), [metadata("one"), metadata("two")])
    with pytest.raises(ConnectorError, match="Ambiguous"):
        source.discover()
    source.config = {**CONFIG, "catalog": "two"}
    assert source.discover()[0][0].catalog == "two"


def test_discovery_respects_exact_schema_allowlist():
    source, _, _ = backend(Reader([]), [metadata(namespace="public"), metadata(namespace="private")])
    assert [table.namespace for table, _ in source.discover()] == ["public"]


def test_connection_failures_are_safe():
    factory = Mock(side_effect=RuntimeError(CONFIG["uri"]))
    source = AdbcBackend(CONFIG, factory)
    with pytest.raises(ConnectorError) as exc:
        source.check()
    assert "secret" not in str(exc.value)


def test_connection_modes_share_generic_backend(monkeypatch):
    manager = Mock()
    monkeypatch.setattr("source_redis_adbc.backend.dbapi.connect", manager)
    monkeypatch.setenv("REDIS_ADBC_LIBRARY", "/driver.so")
    connect(CONFIG)
    args = manager.call_args.kwargs
    assert args["autocommit"] is True
    assert args["entrypoint"] == "AdbcDriverRedisInit"
    assert args["db_kwargs"]["adbc.redis.stream_results"] == "true"
    import adbc_driver_flightsql.dbapi as flight

    gateway = Mock()
    monkeypatch.setattr(flight, "connect", gateway)
    connect({"uri": "grpc+tls://localhost:1234", "connection_type": "flight_sql", "database_options": {"username": "test"}})
    gateway.assert_called_once_with("grpc+tls://localhost:1234", db_kwargs={"username": "test"}, autocommit=True)


@pytest.mark.parametrize(
    "config",
    [
        {},
        {"uri": "http://localhost"},
        {**CONFIG, "batch_size": 0},
        {**CONFIG, "schemas": []},
        {**CONFIG, "database_options": {"uri": "redis://other"}},
        {**CONFIG, "connection_type": "flight_sql"},
        {**CONFIG, "unknown": "secret"},
    ],
)
def test_invalid_config_is_safe(config):
    with pytest.raises(ConnectorError) as exc:
        validate_config(config, SourceRedisAdbc().spec(None).connectionSpecification)
    assert "secret" not in str(exc.value)
