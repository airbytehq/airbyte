#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import base64
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from google.cloud import datastore
from source_datastore.streams import DatastoreStream, _infer_json_type, _key_to_str, _serialize_value


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_key(project, kind, identifier):
    return datastore.Key(kind, identifier, project=project)


def _make_entity(key, properties: dict) -> datastore.Entity:
    entity = datastore.Entity(key=key)
    entity.update(properties)
    return entity


def _make_stream(kind="Product", namespace=None):
    client = MagicMock(spec=datastore.Client)
    return DatastoreStream(client=client, kind=kind, namespace=namespace)


# ---------------------------------------------------------------------------
# _serialize_value
# ---------------------------------------------------------------------------


def test_serialize_datetime_utc():
    dt = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert _serialize_value(dt) == "2024-06-01T12:00:00+00:00"


def test_serialize_datetime_naive_assumed_utc():
    dt = datetime(2024, 6, 1, 12, 0, 0)
    result = _serialize_value(dt)
    assert result.startswith("2024-06-01T12:00:00")


def test_serialize_bytes():
    raw = b"hello"
    assert _serialize_value(raw) == base64.b64encode(raw).decode()


def test_serialize_key():
    key = _make_key("proj", "MyKind", 42)
    result = _serialize_value(key)
    assert "MyKind" in result
    assert "42" in result


def test_serialize_nested_dict():
    result = _serialize_value({"ts": datetime(2024, 1, 1, tzinfo=timezone.utc), "x": 1})
    assert result["ts"] == "2024-01-01T00:00:00+00:00"
    assert result["x"] == 1


def test_serialize_list():
    result = _serialize_value([b"a", b"b"])
    assert result == [base64.b64encode(b"a").decode(), base64.b64encode(b"b").decode()]


def test_serialize_primitive_passthrough():
    assert _serialize_value(42) == 42
    assert _serialize_value("hello") == "hello"
    assert _serialize_value(3.14) == 3.14
    assert _serialize_value(None) is None


# ---------------------------------------------------------------------------
# _infer_json_type
# ---------------------------------------------------------------------------


def test_infer_bool():
    # bool before int
    assert _infer_json_type(True) == {"type": ["null", "boolean"]}


def test_infer_int():
    assert _infer_json_type(42) == {"type": ["null", "integer"]}


def test_infer_float():
    assert _infer_json_type(3.14) == {"type": ["null", "number"]}


def test_infer_datetime():
    dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
    result = _infer_json_type(dt)
    assert result["type"] == ["null", "string"]
    assert result["format"] == "date-time"


def test_infer_bytes():
    result = _infer_json_type(b"data")
    assert result["type"] == ["null", "string"]


def test_infer_string():
    assert _infer_json_type("hello") == {"type": ["null", "string"]}


def test_infer_list():
    assert _infer_json_type([1, 2]) == {"type": ["null", "array"]}


def test_infer_dict():
    assert _infer_json_type({"a": 1}) == {"type": ["null", "object"]}


# ---------------------------------------------------------------------------
# _key_to_str
# ---------------------------------------------------------------------------


def test_key_to_str_with_id():
    key = _make_key("proj", "Order", 99)
    assert _key_to_str(key) == "Order/99"


def test_key_to_str_with_name():
    key = datastore.Key("Product", "sku-001", project="proj")
    assert _key_to_str(key) == "Product/sku-001"


# ---------------------------------------------------------------------------
# DatastoreStream — class properties
# ---------------------------------------------------------------------------


def test_stream_name_lowercased():
    assert _make_stream(kind="MyKind").name == "mykind"


def test_stream_name_spaces_to_underscores():
    assert _make_stream(kind="My Kind").name == "my_kind"


def test_stream_name_hyphens_to_underscores():
    assert _make_stream(kind="my-kind").name == "my_kind"


def test_primary_key():
    assert DatastoreStream.primary_key == "_key"


def test_source_defined_cursor_is_false():
    assert DatastoreStream.source_defined_cursor is False


def test_supported_sync_modes_always_includes_incremental():
    from airbyte_cdk.models import SyncMode

    s = _make_stream()
    assert SyncMode.incremental in s.supported_sync_modes
    assert SyncMode.full_refresh in s.supported_sync_modes


def test_cursor_field_default_empty():
    s = _make_stream()
    assert s.cursor_field == ""


# ---------------------------------------------------------------------------
# get_json_schema — dynamic sampling
# ---------------------------------------------------------------------------


def test_get_json_schema_includes_meta_fields():
    client = MagicMock(spec=datastore.Client)
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client.query.return_value = mock_query

    s = DatastoreStream(client=client, kind="Product", namespace=None)
    schema = s.get_json_schema()

    assert "_key" in schema["properties"]
    assert "_kind" in schema["properties"]
    assert "_namespace" in schema["properties"]
    assert schema.get("additionalProperties") is True


def test_get_json_schema_infers_entity_properties():
    client = MagicMock(spec=datastore.Client)
    key = _make_key("proj", "Product", 1)
    entity = _make_entity(
        key,
        {
            "name": "Widget",
            "price": 9.99,
            "in_stock": True,
            "updated_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        },
    )

    mock_query = MagicMock()
    mock_query.fetch.return_value = [entity]
    client.query.return_value = mock_query

    s = DatastoreStream(client=client, kind="Product", namespace=None)
    schema = s.get_json_schema()
    props = schema["properties"]

    assert props["name"] == {"type": ["null", "string"]}
    assert props["price"] == {"type": ["null", "number"]}
    assert props["in_stock"] == {"type": ["null", "boolean"]}
    assert props["updated_at"]["format"] == "date-time"


def test_get_json_schema_does_not_overwrite_meta_fields():
    """Entity property named '_key' must not overwrite the meta field."""
    client = MagicMock(spec=datastore.Client)
    key = _make_key("proj", "Product", 1)
    entity = _make_entity(key, {"_key": "should not overwrite"})

    mock_query = MagicMock()
    mock_query.fetch.return_value = [entity]
    client.query.return_value = mock_query

    s = DatastoreStream(client=client, kind="Product", namespace=None)
    schema = s.get_json_schema()
    # Meta _key is declared first; entity property should not replace it
    assert "description" in schema["properties"]["_key"]


def test_get_json_schema_samples_limit():
    from source_datastore.streams import _SCHEMA_SAMPLE_SIZE

    client = MagicMock(spec=datastore.Client)
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client.query.return_value = mock_query

    s = DatastoreStream(client=client, kind="Product", namespace=None)
    s.get_json_schema()
    mock_query.fetch.assert_called_once_with(limit=_SCHEMA_SAMPLE_SIZE)


# ---------------------------------------------------------------------------
# read_records
# ---------------------------------------------------------------------------


def test_read_records_full_refresh():
    from airbyte_cdk.models import SyncMode

    client = MagicMock(spec=datastore.Client)
    key = _make_key("proj", "Product", 1)
    entity = _make_entity(key, {"name": "Widget", "price": 9.99})

    mock_query = MagicMock()
    mock_query.fetch.return_value = [entity]
    client.query.return_value = mock_query

    stream = DatastoreStream(client=client, kind="Product", namespace=None)
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

    assert len(records) == 1
    rec = records[0]
    assert rec["_kind"] == "Product"
    assert rec["_namespace"] == ""
    assert rec["name"] == "Widget"
    assert rec["price"] == 9.99
    assert "Product" in rec["_key"]


def test_read_records_sets_active_cursor_from_param():
    from airbyte_cdk.models import SyncMode

    client = MagicMock(spec=datastore.Client)
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client.query.return_value = mock_query

    stream = DatastoreStream(client=client, kind="Product", namespace=None)
    list(stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=["updated_at"]))

    assert stream._active_cursor == "updated_at"
    assert stream.cursor_field == "updated_at"


def test_read_records_serializes_datetime():
    from airbyte_cdk.models import SyncMode

    client = MagicMock(spec=datastore.Client)
    key = _make_key("proj", "Order", 10)
    dt = datetime(2024, 3, 15, 10, 0, 0, tzinfo=timezone.utc)
    entity = _make_entity(key, {"updated_at": dt, "total": 100})

    mock_query = MagicMock()
    mock_query.fetch.return_value = [entity]
    client.query.return_value = mock_query

    stream = DatastoreStream(client=client, kind="Order", namespace="prod")
    records = list(
        stream.read_records(
            sync_mode=SyncMode.full_refresh,
            cursor_field=["updated_at"],
        )
    )

    assert records[0]["updated_at"] == "2024-03-15T10:00:00+00:00"
    assert records[0]["_namespace"] == "prod"


def test_read_records_incremental_adds_filter():
    from airbyte_cdk.models import SyncMode

    client = MagicMock(spec=datastore.Client)
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client.query.return_value = mock_query

    stream = DatastoreStream(client=client, kind="Product", namespace=None)
    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            cursor_field=["updated_at"],
            stream_state={"updated_at": "2024-01-01T00:00:00+00:00"},
        )
    )

    mock_query.add_filter.assert_called_once()


def test_read_records_incremental_no_state_no_filter():
    from airbyte_cdk.models import SyncMode

    client = MagicMock(spec=datastore.Client)
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client.query.return_value = mock_query

    stream = DatastoreStream(client=client, kind="Product", namespace=None)
    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            cursor_field=["updated_at"],
            stream_state={},
        )
    )

    mock_query.add_filter.assert_not_called()


def test_read_records_no_cursor_no_filter():
    from airbyte_cdk.models import SyncMode

    client = MagicMock(spec=datastore.Client)
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client.query.return_value = mock_query

    stream = DatastoreStream(client=client, kind="Product", namespace=None)
    list(stream.read_records(sync_mode=SyncMode.incremental, stream_state={"updated_at": "x"}))

    mock_query.add_filter.assert_not_called()


# ---------------------------------------------------------------------------
# get_updated_state
# ---------------------------------------------------------------------------


def test_get_updated_state_uses_active_cursor():
    from airbyte_cdk.models import SyncMode

    client = MagicMock(spec=datastore.Client)
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client.query.return_value = mock_query

    stream = DatastoreStream(client=client, kind="Product", namespace=None)
    # Simulate that read_records was called first and set the active cursor
    list(stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["updated_at"]))

    state = stream.get_updated_state(
        {"updated_at": "2024-01-01"},
        {"updated_at": "2024-06-01"},
    )
    assert state == {"updated_at": "2024-06-01"}


def test_get_updated_state_keeps_current_if_newer():
    from airbyte_cdk.models import SyncMode

    client = MagicMock(spec=datastore.Client)
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client.query.return_value = mock_query

    stream = DatastoreStream(client=client, kind="Product", namespace=None)
    list(stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["updated_at"]))

    state = stream.get_updated_state(
        {"updated_at": "2024-12-31"},
        {"updated_at": "2024-01-01"},
    )
    assert state == {"updated_at": "2024-12-31"}


def test_get_updated_state_no_active_cursor_returns_empty():
    s = _make_stream()
    state = s.get_updated_state({}, {"updated_at": "2024-01-01"})
    assert state == {}
