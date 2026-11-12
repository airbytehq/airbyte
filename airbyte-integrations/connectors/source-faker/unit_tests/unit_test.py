#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import jsonschema
import pytest
import tomllib
from packaging.specifiers import SpecifierSet
from source_faker import SourceFaker

from airbyte_cdk.models import AirbyteMessage, AirbyteMessageSerializer, ConfiguredAirbyteCatalog, ConfiguredAirbyteStreamSerializer, Type


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

    from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor
    from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob

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


def test_read_users_resumes_from_checkpoint():
    from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor
    from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob

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


USERS_INCREMENTAL_STREAM = {
    "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
    "sync_mode": "incremental",
    "destination_sync_mode": "append_dedup",
}


def _read_users(config, state):
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(USERS_INCREMENTAL_STREAM)])
    messages = list(SourceFaker().read(logger, config, catalog, state))
    user_ids = [message.record.data["id"] for message in messages if message.type is Type.RECORD]
    state_messages = [message.state for message in messages if message.type is Type.STATE]
    return user_ids, state_messages


def test_users_are_all_emitted_again_on_syncs_after_a_completed_sync():
    config = {"count": 10, "records_per_slice": 5, "parallelism": 1, "always_updated": True}
    all_user_ids = list(range(1, 11))

    first_ids, first_states = _read_users(config, [])
    assert first_ids == all_user_ids

    second_ids, second_states = _read_users(config, [first_states[-1]])
    assert second_ids == all_user_ids

    third_ids, third_states = _read_users(config, [second_states[-1]])
    assert third_ids == all_user_ids

    for final_state in (first_states[-1], second_states[-1], third_states[-1]):
        stream_state = final_state.stream.stream_state
        assert stream_state.loop_offset == 10
        assert stream_state.completed is True


@pytest.mark.parametrize(
    "saved_state, count, expected_ids",
    [
        pytest.param(
            {"seed": -1, "updated_at": "2024-01-01T00:00:00+00:00", "loop_offset": 10},
            10,
            list(range(1, 11)),
            id="state_of_a_completed_sync_saved_by_an_earlier_version",
        ),
        pytest.param(
            {"seed": -1, "updated_at": "2024-01-01T00:00:00+00:00", "loop_offset": 10, "completed": True},
            20,
            list(range(1, 21)),
            id="count_raised_after_a_completed_sync",
        ),
    ],
)
def test_users_read_with_saved_state(saved_state, count, expected_ids):
    from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor
    from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob

    config = {"count": count, "records_per_slice": 5, "parallelism": 1, "always_updated": True}
    stream_state = AirbyteStreamState(
        stream_descriptor=StreamDescriptor(name="users", namespace=None), stream_state=AirbyteStateBlob(**saved_state)
    )
    state = [AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=stream_state)]

    user_ids, state_messages = _read_users(config, state)

    assert user_ids == expected_ids
    final_state = state_messages[-1].stream.stream_state
    assert final_state.loop_offset == count
    assert final_state.completed is True


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


def test_pyproject_requires_python_3_11_or_newer():
    pyproject = tomllib.loads((Path(__file__).parent.parent / "pyproject.toml").read_text())
    python_spec = SpecifierSet(pyproject["tool"]["poetry"]["dependencies"]["python"])
    assert "3.10.12" not in python_spec
    assert "3.11.0" in python_spec
