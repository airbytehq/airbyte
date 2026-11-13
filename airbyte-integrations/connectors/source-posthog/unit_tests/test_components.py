#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from unittest.mock import Mock

import pytest
from source_posthog import SourcePosthog
from source_posthog.components import EventsPerProjectCursor

from airbyte_cdk.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, Type
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.types import Record


CONFIG = {"api_key": "api_key", "start_date": "2021-01-01T00:00:00Z"}


def _cursor(stream_state, project_ids=(2331,), message_repository=None):
    return EventsPerProjectCursor(
        stream_name="events",
        partition_router=ListPartitionRouter(values=list(project_ids), cursor_field="project_id", config={}, parameters={}),
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
        end_datetime=MinMaxDatetime(datetime="2021-02-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
        step=datetime.timedelta(days=10),
        cursor_granularity=datetime.timedelta(microseconds=1),
        datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
        cursor_datetime_formats=[],
        config={},
        stream_state=stream_state,
        message_repository=message_repository or InMemoryMessageRepository(),
        connector_state_manager=ConnectorStateManager(),
    )


def _partition(stream_slice):
    partition = Mock()
    partition.to_slice.return_value = stream_slice
    return partition


def _read_slice(cursor, stream_slice, records):
    for record in records:
        cursor.observe(Record(data=record, stream_name="events", associated_slice=stream_slice))
    cursor.close_partition(_partition(stream_slice))


@pytest.mark.parametrize(
    "test_name, initial_state, last_record, expected_state",
    [
        ("test_empty", {}, {}, {}),
        (
            "test_set_initial_state",
            {"2331": {"timestamp": "2021-01-01T00:00:00.00+0000"}},
            {},
            {"2331": {"timestamp": "2021-01-01T00:00:00.00+0000"}},
        ),
        (
            "test_update_empty_state",
            {},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state",
            {"2331": {"timestamp": "2021-01-01T10:00:00.00+0000"}},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state_newly",
            {"2331": {"timestamp": "2021-01-01T22:00:00.00+0000"}},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T22:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state_old_style",
            {"timestamp": "2021-01-01T10:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}, "timestamp": "2021-01-01T10:00:00.00+0000"},
        ),
    ],
)
def test_update_cursor(test_name, initial_state, last_record, expected_state):
    cursor = _cursor(initial_state)
    first_slice = next(iter(cursor.stream_slices()))

    _read_slice(cursor, first_slice, [last_record] if last_record else [])

    assert cursor.state == expected_state


@pytest.mark.parametrize(
    "test_name, stream_state, expected_stream_slices",
    [
        (
            "test_empty_state",
            {},
            [
                {"end_time": "2021-01-10T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T00:00:00.000000+0000"},
                {"end_time": "2021-01-20T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-10T23:59:59.999999+0000"},
                {"end_time": "2021-01-30T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-20T23:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-30T23:59:59.999999+0000"},
            ],
        ),
        (
            "test_state",
            {"2331": {"timestamp": "2021-01-01T17:00:00.000000+0000"}},
            [
                {"end_time": "2021-01-11T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T17:00:00.000000+0000"},
                {"end_time": "2021-01-21T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-11T16:59:59.999999+0000"},
                {"end_time": "2021-01-31T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-21T16:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-31T16:59:59.999999+0000"},
            ],
        ),
        (
            "test_old_stype_state",
            {"timestamp": "2021-01-01T17:00:00.000000+0000"},
            [
                {"end_time": "2021-01-11T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T17:00:00.000000+0000"},
                {"end_time": "2021-01-21T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-11T16:59:59.999999+0000"},
                {"end_time": "2021-01-31T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-21T16:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-31T16:59:59.999999+0000"},
            ],
        ),
        (
            "test_state_for_one_slice",
            {"2331": {"timestamp": "2021-01-27T17:00:00.000000+0000"}},
            [{"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-27T17:00:00.000000+0000"}],
        ),
    ],
)
def test_stream_slices(test_name, stream_state, expected_stream_slices):
    cursor = _cursor(stream_state)
    assert [dict(stream_slice) for stream_slice in cursor.stream_slices()] == expected_stream_slices


def test_project_without_state_starts_from_start_date():
    cursor = _cursor({"1": {"timestamp": "2021-01-27T17:00:00.000000+0000"}}, project_ids=(1, 2))

    first_slice_per_project = {}
    for stream_slice in cursor.stream_slices():
        first_slice_per_project.setdefault(stream_slice["project_id"], stream_slice["start_time"])

    assert first_slice_per_project == {"1": "2021-01-27T17:00:00.000000+0000", "2": "2021-01-01T00:00:00.000000+0000"}


def test_state_only_moves_past_a_slice_once_all_earlier_slices_of_the_project_are_read():
    cursor = _cursor({}, project_ids=(1, 2))
    slices = list(cursor.stream_slices())
    project_1_slices = [s for s in slices if s["project_id"] == "1"]
    project_2_slices = [s for s in slices if s["project_id"] == "2"]

    # The second slice of project 1 finishes before the first one
    _read_slice(cursor, project_1_slices[1], [{"timestamp": "2021-01-15T00:00:00.000000+0000"}])
    _read_slice(cursor, project_2_slices[0], [{"timestamp": "2021-01-02T00:00:00.000000+0000"}])
    assert cursor.state == {"2": {"timestamp": "2021-01-02T00:00:00.000000+0000"}}

    _read_slice(cursor, project_1_slices[0], [{"timestamp": "2021-01-05T00:00:00.000000+0000"}])
    assert cursor.state == {
        "1": {"timestamp": "2021-01-15T00:00:00.000000+0000"},
        "2": {"timestamp": "2021-01-02T00:00:00.000000+0000"},
    }


def test_most_recent_record_of_a_slice_is_kept_in_the_state():
    cursor = _cursor({})
    first_slice = next(iter(cursor.stream_slices()))

    # The API returns the newest events first
    _read_slice(
        cursor,
        first_slice,
        [{"timestamp": "2021-01-03T00:00:00.000000+0000"}, {"timestamp": "2021-01-02T00:00:00.000000+0000"}, {"id": "no timestamp"}],
    )

    assert cursor.state == {"2331": {"timestamp": "2021-01-03T00:00:00.000000+0000"}}


def test_state_message_is_emitted_when_a_slice_is_read():
    message_repository = InMemoryMessageRepository()
    cursor = _cursor({}, message_repository=message_repository)
    first_slice = next(iter(cursor.stream_slices()))

    _read_slice(cursor, first_slice, [{"timestamp": "2021-01-03T00:00:00.000000+0000"}])

    state_messages = [message for message in message_repository.consume_queue() if message.type == Type.STATE]
    assert [message.state.stream.stream_state.__dict__ for message in state_messages] == [
        {"2331": {"timestamp": "2021-01-03T00:00:00.000000+0000"}}
    ]


def test_events_stream_uses_per_project_cursor_with_incoming_state():
    stream_state = {"1": {"timestamp": "2021-01-27T17:00:00.000000+0000"}}
    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name="events"), stream_state=AirbyteStateBlob(stream_state)),
        )
    ]
    source = SourcePosthog(config=CONFIG, state=state)

    events_stream = next(stream for stream in source.streams(CONFIG) if stream.name == "events")

    assert isinstance(events_stream.cursor, EventsPerProjectCursor)
    assert events_stream.cursor.state == stream_state
    assert events_stream.cursor_field == "timestamp"
