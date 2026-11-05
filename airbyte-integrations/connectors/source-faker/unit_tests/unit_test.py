#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime

import jsonschema
import pytest
from pytest_mock import MockerFixture
from source_faker import SourceFaker

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteStateMessage,
    AirbyteStateMessageSerializer,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStreamSerializer,
    StreamDescriptor,
    Type,
)
from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob


class MockLogger:
    def debug(a, b, **kwargs):
        return None

    def info(a, b, **kwargs):
        return None

    def exception(a, b, **kwargs):
        print(b)
        return None

    def isEnabledFor(a, b, **kwargs):
        return False


logger = MockLogger()


def schemas_are_valid():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=catalog))
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)


def test_source_streams():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=catalog))
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    assert len(schemas) == 3
    assert schemas[1]["properties"] == {
        "id": {"type": "integer"},
        "created_at": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"},
        "updated_at": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"},
        "name": {"type": "string"},
        "title": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"},
        "telephone": {"type": "string"},
        "gender": {"type": "string"},
        "language": {"type": "string"},
        "academic_degree": {"type": "string"},
        "nationality": {"type": "string"},
        "occupation": {"type": "string"},
        "height": {"type": "string"},
        "blood_type": {"type": "string"},
        "weight": {"type": "integer"},
        "address": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "country_code": {"type": "string"},
                "postal_code": {"type": "string"},
                "province": {"type": "string"},
                "state": {"type": "string"},
                "street_name": {"type": "string"},
                "street_number": {"type": "string"},
            },
        },
    }


def test_read_small_random_data():
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1}
    stream_dict = {
        "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    estimate_row_count = 0
    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.TRACE:
            estimate_row_count = estimate_row_count + 1
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert estimate_row_count == 4
    assert record_rows_count == 10
    assert state_rows_count == 1


def test_read_always_updated():
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1, "always_updated": False}
    stream_dict = {
        "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1

    assert record_rows_count == 10

    stream_descriptor = StreamDescriptor(name="users", namespace=None)
    stream_state = AirbyteStreamState(stream_descriptor=stream_descriptor, stream_state=AirbyteStateBlob(updated_at="something"))
    state = [AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=stream_state)]
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1

    assert record_rows_count == 0


def test_read_products():
    source = SourceFaker()
    config = {"count": 999, "parallelism": 1}
    stream_dict = {
        "stream": {"name": "products", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["full_refresh"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    estimate_row_count = 0
    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.TRACE:
            estimate_row_count = estimate_row_count + 1
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert estimate_row_count == 4
    assert record_rows_count == 100  # only 100 products, no matter the count
    assert state_rows_count in {1, 2}, "Expected 1 or 2 state messages per stream."


def test_read_big_random_data():
    source = SourceFaker()
    config = {"count": 1000, "records_per_slice": 100, "parallelism": 1}
    stream_dicts = [
        {
            "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
        {
            "stream": {"name": "products", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["full_refresh"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
    ]
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict) for stream_dict in stream_dicts])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert record_rows_count == 1000 + 100  # 1000 users, and 100 products
    assert state_rows_count == 11


def test_with_purchases():
    source = SourceFaker()
    config = {"count": 1000, "parallelism": 1}
    stream_dicts = [
        {
            "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
        {
            "stream": {"name": "products", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["full_refresh"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
        {
            "stream": {"name": "purchases", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
    ]
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict) for stream_dict in stream_dicts])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert record_rows_count > 1000 + 100  # should be greater than 1000 users, and 100 products
    assert state_rows_count > 10 + 1  # should be greater than 1000/100, and one state for the products


def test_read_with_seed():
    """
    This test asserts that setting a seed always returns the same values
    """

    source = SourceFaker()
    config = {"count": 1, "seed": 100, "parallelism": 1}
    stream_dict = {
        "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    records = [row for row in iterator if row.type is Type.RECORD]
    assert records[0].record.data["occupation"] == "Sheriff Principal"
    assert records[0].record.data["email"] == "alleged2069+1@example.com"


def test_ensure_no_purchases_without_users():
    with pytest.raises(ValueError):
        source = SourceFaker()
        config = {"count": 100, "parallelism": 1}
        stream_dict = {
            "stream": {"name": "purchases", "json_schema": {"type": "object", "properties": {}}},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        }
        catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
        state = {}
        iterator = source.read(logger, config, catalog, state)
        iterator.__next__()


def test_read_users_resumes_from_checkpoint():
    source = SourceFaker()
    config = {"count": 10, "records_per_slice": 5, "parallelism": 1}
    stream_dict = {
        "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    stream_state = AirbyteStreamState(
        stream_descriptor=StreamDescriptor(name="users", namespace=None),
        stream_state=AirbyteStateBlob(updated_at="2024-01-01T00:00:00+00:00", loop_offset=5),
    )
    state = [AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=stream_state)]
    iterator = source.read(logger, config, catalog, state)

    records = [row.record.data for row in iterator if row.type is Type.RECORD]
    assert [record["id"] for record in records] == [6, 7, 8, 9, 10]


@pytest.fixture
def users_catalog() -> ConfiguredAirbyteCatalog:
    stream_dict = {
        "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "append_dedup",
        "cursor_field": ["updated_at"],
        "primary_key": [["id"]],
    }
    return ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])


@pytest.mark.parametrize(
    "always_updated,count,records_per_slice,parallelism",
    [(True, 1000, 1000, 4), (True, 10, 3, 1), (False, 10, 3, 1)],
)
def test_read_users_consecutive_syncs(
    users_catalog: ConfiguredAirbyteCatalog,
    mocker: MockerFixture,
    always_updated: bool,
    count: int,
    records_per_slice: int,
    parallelism: int,
) -> None:
    config = {
        "count": count,
        "seed": -1,
        "records_per_slice": records_per_slice,
        "always_updated": always_updated,
        "parallelism": parallelism,
    }
    clock = mocker.patch("source_faker.user_generator.datetime")
    state: list[AirbyteStateMessage] = []
    for sync in range(3):
        clock.datetime.now.return_value = datetime(2026, 1, sync + 1)
        messages = list(SourceFaker().read(logging.getLogger(__name__), config, users_catalog, state))
        records = [message.record.data for message in messages if message.type is Type.RECORD and message.record is not None]
        expected_count = count if sync == 0 or always_updated else 0
        assert len(records) == expected_count
        assert [record["id"] for record in records] == list(range(1, expected_count + 1))
        assert all(record["updated_at"] == f"2026-01-0{sync + 1}T00:00:00+00:00" for record in records)
        final_state = [message.state for message in messages if message.type is Type.STATE and message.state is not None][-1]
        serialized_state = AirbyteStateMessageSerializer.dump(final_state)
        state = [AirbyteStateMessageSerializer.load(serialized_state)]
        assert serialized_state["stream"]["stream_state"]["loop_offset"] == count


@pytest.mark.parametrize("loop_offset", [None, 0, 5, 10, 12])
def test_read_users_saved_offsets(users_catalog: ConfiguredAirbyteCatalog, loop_offset: int | None) -> None:
    config = {"count": 10, "records_per_slice": 3, "parallelism": 1, "always_updated": True}
    saved_state = {"seed": -1, "updated_at": "2024-01-01T00:00:00+00:00"}
    if loop_offset is not None:
        saved_state["loop_offset"] = loop_offset
    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="users"),
                stream_state=AirbyteStateBlob(**saved_state),
            ),
        )
    ]
    messages = list(SourceFaker().read(logging.getLogger(__name__), config, users_catalog, state))
    records = [message.record.data for message in messages if message.type is Type.RECORD and message.record is not None]
    first_id = 6 if loop_offset == 5 else 1
    assert [record["id"] for record in records] == list(range(first_id, 11))
    estimates = [
        message.trace.estimate
        for message in messages
        if message.type is Type.TRACE and message.trace is not None and message.trace.estimate is not None
    ]
    assert estimates[0].row_estimate == len(records)
    final_state = [message.state for message in messages if message.type is Type.STATE and message.state is not None][-1]
    assert AirbyteStateMessageSerializer.dump(final_state)["stream"]["stream_state"]["loop_offset"] == 10
