import pendulum
import pytest
from airbyte_cdk.models import AirbyteMessage, Type, AirbyteRecordMessage, ConfiguredAirbyteStream, AirbyteStream
from source_acceptance_test.tests.test_incremental import records_with_state


@pytest.fixture(name="simple_state")
def simple_state_fixture():
    return {
        "my_stream": {
            "id": 11,
            "ts_created": "2014-01-01T22:03:11",
            "ts_updated": "2015-01-01T22:03:11",
        }
    }


@pytest.fixture(name="nested_state")
def nested_state_fixture(simple_state):
    return {
        "my_stream": {
            "some_account_id": simple_state["my_stream"]
        }
    }


@pytest.fixture(name="singer_state")
def singer_state_fixture(simple_state):
    return {
        "bookmarks": simple_state
    }


@pytest.fixture(name="stream_schema")
def stream_schema_fixture():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": {
                "type": "integer"
            },
            "ts_created": {
                "type": "string",
                "format": "datetime"
            },
            "nested": {
                "type": "object",
                "properties": {
                    "ts_updated": {
                        "type": "string",
                        "format": "date"
                    }
                }
            }
        }
    }


@pytest.fixture(name="stream_mapping")
def stream_mapping_fixture(stream_schema):
    return {
        "my_stream": ConfiguredAirbyteStream(stream=AirbyteStream(json_schema=stream_schema))
    }


@pytest.fixture(name="records")
def records_fixture():
    return [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="my_stream", data={
            "id": 1, "ts_created": "2015-11-01T22:03:11", "nested": {"ts_updated": "2015-05-01"}
        }))
    ]


def test_simple_path(records, stream_mapping, simple_state):
    paths = ["id"]

    result = records_with_state(records=records, state=simple_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value = next(result)

    assert record_value == 1, "record value must be correctly found"
    assert state_value == 11, "state value must be correctly found"


def test_nested_path(records, stream_mapping, nested_state):
    paths = ["nested", "ts_updated"]

    result = records_with_state(records=records, state=nested_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value = next(result)

    assert record_value == pendulum.datetime(2015, 5, 1), "record value must be correctly found"
    assert state_value == pendulum.datetime(2015, 1, 1, 22, 3, 11), "state value must be correctly found"


def test_nested_path_unknown(records, stream_mapping, simple_state):
    paths = ["id"]

    result = records_with_state(records=records, state=simple_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value = next(result)

    assert record_value == 1, "record value must be correctly found"
    assert state_value == 11, "state value must be correctly found"


def test_absolute_path(records, stream_mapping, singer_state):
    paths = ["bookmarks", "my_stream", "ts_created"]

    result = records_with_state(records=records, state=singer_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value = next(result)

    assert record_value == 1, "record value must be correctly found"
    assert state_value == 11, "state value must be correctly found"
