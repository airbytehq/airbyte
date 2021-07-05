#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import pendulum
import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
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
    return {"my_stream": {"some_account_id": simple_state["my_stream"]}}


@pytest.fixture(name="singer_state")
def singer_state_fixture(simple_state):
    return {"bookmarks": simple_state}


@pytest.fixture(name="stream_schema")
def stream_schema_fixture():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "ts_created": {"type": "string", "format": "datetime"},
            "nested": {"type": "object", "properties": {"ts_updated": {"type": "string", "format": "date"}}},
        },
    }


@pytest.fixture(name="stream_mapping")
def stream_mapping_fixture(stream_schema):
    return {
        "my_stream": ConfiguredAirbyteStream(
            stream=AirbyteStream(name="my_stream", json_schema=stream_schema),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.append,
        )
    }


@pytest.fixture(name="records")
def records_fixture():
    return [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="my_stream",
                data={"id": 1, "ts_created": "2015-11-01T22:03:11", "nested": {"ts_updated": "2015-05-01"}},
                emitted_at=0,
            ),
        )
    ]


def test_simple_path(records, stream_mapping, simple_state):
    stream_mapping["my_stream"].cursor_field = ["id"]
    paths = {"my_stream": ["id"]}

    result = records_with_state(records=records, state=simple_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value = next(result)

    assert record_value == 1, "record value must be correctly found"
    assert state_value == 11, "state value must be correctly found"


def test_nested_path(records, stream_mapping, nested_state):
    stream_mapping["my_stream"].cursor_field = ["nested", "ts_updated"]
    paths = {"my_stream": ["some_account_id", "ts_updated"]}

    result = records_with_state(records=records, state=nested_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value = next(result)

    assert record_value == pendulum.datetime(2015, 5, 1), "record value must be correctly found"
    assert state_value == pendulum.datetime(2015, 1, 1, 22, 3, 11), "state value must be correctly found"


def test_nested_path_unknown(records, stream_mapping, simple_state):
    stream_mapping["my_stream"].cursor_field = ["ts_created"]
    paths = {"my_stream": ["unknown", "ts_created"]}

    result = records_with_state(records=records, state=simple_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    with pytest.raises(KeyError):
        next(result)


def test_absolute_path(records, stream_mapping, singer_state):
    stream_mapping["my_stream"].cursor_field = ["ts_created"]
    paths = {"my_stream": ["bookmarks", "my_stream", "ts_created"]}

    result = records_with_state(records=records, state=singer_state, stream_mapping=stream_mapping, state_cursor_paths=paths)
    record_value, state_value = next(result)

    assert record_value == pendulum.datetime(2015, 11, 1, 22, 3, 11), "record value must be correctly found"
    assert state_value == pendulum.datetime(2014, 1, 1, 22, 3, 11), "state value must be correctly found"
