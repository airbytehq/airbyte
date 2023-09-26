#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from contextlib import nullcontext as does_not_raise
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from unittest.mock import MagicMock, patch

import pendulum
import pytest
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    Type,
)
from connector_acceptance_test.config import Config, EmptyStreamConfiguration, IncrementalConfig
from connector_acceptance_test.tests import test_incremental
from connector_acceptance_test.tests.test_incremental import TestIncremental as _TestIncremental
from connector_acceptance_test.tests.test_incremental import future_state_configuration_fixture, future_state_fixture

pytestmark = [
    pytest.mark.anyio,
]


def build_messages_from_record_data(stream: str, records: list[dict]) -> list[AirbyteMessage]:
    return [build_record_message(stream, data) for data in records]


def build_record_message(stream: str, data: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=111))


def build_state_message(state: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=state))


def build_per_stream_state_message(
    descriptor: StreamDescriptor, stream_state: Optional[dict[str, Any]], data: Optional[dict[str, Any]] = None
) -> AirbyteMessage:
    if data is None:
        data = stream_state
    stream_state_blob = AirbyteStateBlob.parse_obj(stream_state) if stream_state else None
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM, stream=AirbyteStreamState(stream_descriptor=descriptor, stream_state=stream_state_blob), data=data
        ),
    )


@pytest.mark.parametrize("cursor_type", ["date", "string"])
@pytest.mark.parametrize(
    "records1, records2, latest_state, expected_error",
    [
        (
            [{"date": "2020-01-01"}, {"date": "2020-01-02"}],
            [],
            "2020-01-01",
            does_not_raise()
        ),
        (
            [{"date": "2020-01-02"}, {"date": "2020-01-03"}],
            [],
            "2020-01-02",
            does_not_raise(),
        ),
        (
            [{"date": "2020-01-01"}, {"date": "2020-01-02"}],
            [{"date": "2020-01-02"}, {"date": "2020-01-03"}],
            "2020-01-03",
            does_not_raise(),
        ),
        (
            [],
            [{"date": "2020-01-01"}],
            "2020-01-04",
            pytest.raises(AssertionError, match="First Read should produce at least one record"),
        ),
        (
            [{"date": "2020-01-01"}, {"date": "2020-01-02"}],
            [{"date": "2020-01-01"}, {"date": "2020-01-02"}],
            "2020-01-05",
            pytest.raises(AssertionError, match="Records should change between reads but did not."),
        ),
        (
            [{"date": "2020-01-02"}, {"date": "2020-01-03"}],
            [],
            "2020-01-06",
            does_not_raise(),
        ),
        (
            [{"date": "2020-01-01"}],
            [{"date": "2020-01-02"}],
            "2020-01-07",
            does_not_raise(),
        ),
        (
            [{"date": "2020-01-01"}],
            [{"date": "2020-01-02"}],
            "someunparseablenonsensestate",
            does_not_raise(),
        ),
    ],
)
@pytest.mark.parametrize(
    "run_per_stream_test",
    [
        pytest.param(False, id="test_two_sequential_reads_using_a_mock_connector_emitting_legacy_state"),
        pytest.param(True, id="test_two_sequential_reads_using_a_mock_connector_emitting_per_stream_state"),
    ],
)
async def test_incremental_two_sequential_reads(
    mocker, records1, records2, latest_state, cursor_type, expected_error, run_per_stream_test
):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream",
                    json_schema={"type": "object", "properties": {"date": {"type": cursor_type}}},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.overwrite,
                cursor_field=["date"],
            )
        ]
    )

    if run_per_stream_test:
        call_read_output_messages = [
            *build_messages_from_record_data("test_stream", records1),
            build_per_stream_state_message(descriptor=StreamDescriptor(name="test_stream"), stream_state={"date": latest_state}),
        ]
        call_read_with_state_output_messages = build_messages_from_record_data("test_stream", records2)
    else:
        call_read_output_messages = [
            *build_messages_from_record_data("test_stream", records1),
            build_state_message({"date": latest_state}),
        ]
        call_read_with_state_output_messages = build_messages_from_record_data("test_stream", records2)

    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read = mocker.AsyncMock(return_value=call_read_output_messages)
    docker_runner_mock.call_read_with_state = mocker.AsyncMock(return_value=call_read_with_state_output_messages)

    t = _TestIncremental()
    with expected_error:
        await t.test_two_sequential_reads(
            connector_config=MagicMock(),
            configured_catalog_for_incremental=catalog,
            docker_runner=docker_runner_mock,
        )


@pytest.mark.parametrize(
    "first_records, subsequent_records, expected_error",
    [
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
            ],
            does_not_raise(),
            id="test_incremental_with_2_states",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
            ],
            pytest.raises(AssertionError, match="First Read should produce at least one record"),
            id="test_incremental_no_record_on_first_read_raises_error",
        ),
        pytest.param(
            [
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
            ],
            pytest.raises(AssertionError, match="First Read should produce at least one state"),
            id="test_incremental_no_state_on_first_read_raises_error",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-13"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-13"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                ],
            ],
            does_not_raise(),
            id="test_first_incremental_only_younger_records",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-04"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-05"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-04"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-05"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ]
            ],
            pytest.raises(AssertionError, match="Records for subsequent reads with new state should be different"),
            id="test_incremental_returns_identical",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-12"}},
                {
                    "type": Type.STATE,
                    "name": "test_stream_2",
                    "stream_state": {"date": "2022-05-13"},
                    "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}},
                },
                {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-13"}},
                {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-14"}},
                {
                    "type": Type.STATE,
                    "name": "test_stream_2",
                    "stream_state": {"date": "2022-05-15"},
                    "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}},
                },
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-12"}},
                    {
                        "type": Type.STATE,
                        "name": "test_stream_2",
                        "stream_state": {"date": "2022-05-13"},
                        "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}},
                    },
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-13"}},
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-14"}},
                    {
                        "type": Type.STATE,
                        "name": "test_stream_2",
                        "stream_state": {"date": "2022-05-15"},
                        "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}},
                    },
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-12"}},
                    {
                        "type": Type.STATE,
                        "name": "test_stream_2",
                        "stream_state": {"date": "2022-05-13"},
                        "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}},
                    },
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-13"}},
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-14"}},
                    {
                        "type": Type.STATE,
                        "name": "test_stream_2",
                        "stream_state": {"date": "2022-05-15"},
                        "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}},
                    },
                ],
                [
                    {
                        "type": Type.STATE,
                        "name": "test_stream_2",
                        "stream_state": {"date": "2022-05-13"},
                        "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-13"}},
                    },
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-13"}},
                    {"type": Type.RECORD, "name": "test_stream_2", "data": {"date": "2022-05-14"}},
                    {
                        "type": Type.STATE,
                        "name": "test_stream_2",
                        "stream_state": {"date": "2022-05-15"},
                        "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}},
                    },
                ],
                [
                    {
                        "type": Type.STATE,
                        "name": "test_stream_2",
                        "stream_state": {"date": "2022-05-15"},
                        "data": {"test_stream": {"date": "2022-05-11"}, "test_stream_2": {"date": "2022-05-15"}},
                    },
                ],
            ],
            does_not_raise(),
            id="test_incremental_with_multiple_streams",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": None},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}},
                ],
            ],
            does_not_raise(),
            id="test_incremental_with_none_state",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
            ],
            [
                [],
            ],
            does_not_raise(),
            id="test_incremental_with_empty_second_read",
        ),
    ],
)
@pytest.mark.parametrize(
    "run_per_stream_test",
    [
        pytest.param(False, id="test_read_with_multiple_states_using_a_mock_connector_emitting_legacy_state"),
        pytest.param(True, id="test_read_with_multiple_states_using_a_mock_connector_emitting_per_stream_state"),
    ],
)
async def test_per_stream_read_with_multiple_states(mocker, first_records, subsequent_records, expected_error, run_per_stream_test):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream",
                    json_schema={"type": "object", "properties": {"date": {"type": "date"}}},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.overwrite,
                cursor_field=["date"],
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream_2",
                    json_schema={"type": "object", "properties": {"date": {"type": "date"}}},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.overwrite,
                cursor_field=["date"],
            ),
        ]
    )

    if run_per_stream_test:
        call_read_output_messages = [
            build_per_stream_state_message(
                descriptor=StreamDescriptor(name=record["name"]), stream_state=record["stream_state"], data=record.get("data", None)
            )
            if record["type"] == Type.STATE
            else build_record_message(record["name"], record["data"])
            for record in list(first_records)
        ]
        call_read_with_state_output_messages = [
            [
                build_per_stream_state_message(
                    descriptor=StreamDescriptor(name=record["name"]), stream_state=record["stream_state"], data=record.get("data", None)
                )
                if record["type"] == Type.STATE
                else build_record_message(stream=record["name"], data=record["data"])
                for record in state_records_group
            ]
            for state_records_group in list(subsequent_records)
        ]
    else:
        call_read_output_messages = [
            build_state_message(state=record.get("data") or {record["name"]: record["stream_state"]})
            if record["type"] == Type.STATE
            else build_record_message(stream=record["name"], data=record["data"])
            for record in list(first_records)
        ]
        call_read_with_state_output_messages = [
            [
                build_state_message(state=record.get("data") or {record["name"]: record["stream_state"]})
                if record["type"] == Type.STATE
                else build_record_message(stream=record["name"], data=record["data"])
                for record in state_records_group
            ]
            for state_records_group in list(subsequent_records)
        ]

    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read = mocker.AsyncMock(return_value=call_read_output_messages)
    docker_runner_mock.call_read_with_state = mocker.AsyncMock(side_effect=call_read_with_state_output_messages)

    t = _TestIncremental()
    # test if skipped
    with expected_error:
        await t.test_read_sequential_slices(
            connector_config=MagicMock(),
            configured_catalog_for_incremental=catalog,
            docker_runner=docker_runner_mock,
            inputs=IncrementalConfig(),
        )


async def test_config_skip_test(mocker):
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read = mocker.AsyncMock(return_value=[])
    t = _TestIncremental()
    with patch.object(pytest, "skip", return_value=None):
        await t.test_read_sequential_slices(
            inputs=IncrementalConfig(skip_comprehensive_incremental_tests=True),
            connector_config=MagicMock(),
            configured_catalog_for_incremental=ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream(
                            name="test_stream",
                            json_schema={"type": "object", "properties": {"date": {"type": "date"}}},
                            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                        ),
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.overwrite,
                        cursor_field=["date"],
                    )
                ]
            ),
            docker_runner=docker_runner_mock,
        )

    # This is guaranteed to fail when the test gets executed
    docker_runner_mock.call_read.assert_not_called()

async def test_state_skip_test(mocker):
    docker_runner_mock = MagicMock()

    first_records = [
        {"type": Type.STATE, "name": "test_stream", "stream_state": {}},
        {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
        {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
        {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-09"}},
        {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
        {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
        {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
        {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
    ]

    call_read_output_messages = [
        build_per_stream_state_message(
            descriptor=StreamDescriptor(name=record["name"]), stream_state=record["stream_state"], data=record.get("data", None)
        )
        if record["type"] == Type.STATE
        else build_record_message(record["name"], record["data"])
        for record in list(first_records)
    ]

    # There needs to be at least 3 state messages for the test to run
    docker_runner_mock.call_read = mocker.AsyncMock(return_value=call_read_output_messages)

    t = _TestIncremental()
    with patch.object(pytest, "skip", return_value=None):
        await t.test_read_sequential_slices(
            inputs=IncrementalConfig(),
            connector_config=MagicMock(),
            configured_catalog_for_incremental=ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream(
                            name="test_stream",
                            json_schema={"type": "object", "properties": {"date": {"type": "date"}}},
                            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                        ),
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.overwrite,
                        cursor_field=["date"],
                    )
                ]
            ),
            docker_runner=docker_runner_mock,
        )

    # This is guaranteed to fail when the test gets executed
    docker_runner_mock.call_read.assert_called()
    docker_runner_mock.call_read_with_state.assert_not_called()


@pytest.mark.parametrize(
    "read_output, expectation",
    [
        pytest.param([], pytest.raises(AssertionError), id="Error because incremental stream should always emit state messages"),
        pytest.param(
            [
                AirbyteMessage(
                    type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"date": "2022-10-04"}, emitted_at=111)
                ),
                AirbyteMessage(
                    type=Type.STATE,
                    state=AirbyteStateMessage(
                        type=AirbyteStateType.STREAM,
                        stream=AirbyteStreamState(
                            stream_descriptor=StreamDescriptor(name="test_stream"),
                            stream_state=AirbyteStateBlob.parse_obj({"date": "2022-10-04"}),
                        ),
                        data={"date": "2022-10-04"},
                    ),
                ),
            ],
            pytest.raises(AssertionError),
            id="Error because incremental sync with abnormally large state value should not produce record.",
        ),
        pytest.param(
            [
                AirbyteMessage(
                    type=Type.STATE,
                    state=AirbyteStateMessage(
                        type=AirbyteStateType.STREAM,
                        stream=AirbyteStreamState(
                            stream_descriptor=StreamDescriptor(name="test_stream"),
                            stream_state=AirbyteStateBlob.parse_obj({"date": "2022-10-04"}),
                        ),
                        data={"date": "2022-10-04"},
                    ),
                )
            ],
            does_not_raise(),
        ),
    ],
)
async def test_state_with_abnormally_large_values(mocker, read_output, expectation):
    docker_runner_mock = mocker.MagicMock()
    docker_runner_mock.call_read_with_state = mocker.AsyncMock(return_value=read_output)
    t = _TestIncremental()
    with expectation:
        await t.test_state_with_abnormally_large_values(
            connector_config=mocker.MagicMock(),
            configured_catalog=ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=AirbyteStream(
                            name="test_stream",
                            json_schema={"type": "object", "properties": {"date": {"type": "date"}}},
                            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                        ),
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.overwrite,
                        cursor_field=["date"],
                    )
                ]
            ),
            future_state=mocker.MagicMock(),
            docker_runner=docker_runner_mock,
        )


@pytest.mark.parametrize(
    "test_strictness_level, inputs, expect_fail, expect_skip",
    [
        pytest.param(
            Config.TestStrictnessLevel.high,
            MagicMock(future_state=MagicMock(future_state_path="my_future_state_path", missing_streams=["foo", "bar"], bypass_reason=None)),
            False,
            False,
            id="high test strictness level, future_state_path and missing streams are defined: run the test.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.low,
            MagicMock(future_state=MagicMock(future_state_path="my_future_state_path", missing_streams=["foo", "bar"], bypass_reason=None)),
            False,
            False,
            id="low test strictness level, future_state_path and missing_streams are defined: run the test.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            MagicMock(future_state=MagicMock(future_state_path=None, bypass_reason=None)),
            True,
            False,
            id="high test strictness level, future_state_path and missing streams are defined: fail the test.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.low,
            MagicMock(future_state=MagicMock(future_state_path=None, bypass_reason=None)),
            False,
            True,
            id="low test strictness level, future_state_path not defined: skip the test.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            MagicMock(future_state=MagicMock(bypass_reason="valid bypass reason")),
            False,
            True,
            id="high test strictness level, bypass_reason: skip test.",
        ),
    ],
)
def test_future_state_configuration_fixture(mocker, test_strictness_level, inputs, expect_fail, expect_skip):
    mocker.patch.object(test_incremental.pytest, "fail")
    mocker.patch.object(test_incremental.pytest, "skip")
    output = future_state_configuration_fixture.__wrapped__(inputs, "base_path", test_strictness_level)
    if not expect_fail and not expect_skip:
        assert output == (Path("base_path/my_future_state_path"), ["foo", "bar"])
    if expect_fail:
        test_incremental.pytest.fail.assert_called_once()
        test_incremental.pytest.skip.assert_not_called()
    if expect_skip:
        test_incremental.pytest.skip.assert_called_once()
        test_incremental.pytest.fail.assert_not_called()


TEST_AIRBYTE_STREAM_A = AirbyteStream(
    name="test_stream_a", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
)
TEST_AIRBYTE_STREAM_B = AirbyteStream(
    name="test_stream_b", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
)

TEST_CONFIGURED_AIRBYTE_STREAM_A = ConfiguredAirbyteStream(
    stream=TEST_AIRBYTE_STREAM_A,
    sync_mode=SyncMode.incremental,
    destination_sync_mode=DestinationSyncMode.overwrite,
)

TEST_CONFIGURED_AIRBYTE_STREAM_B = ConfiguredAirbyteStream(
    stream=TEST_AIRBYTE_STREAM_B,
    sync_mode=SyncMode.incremental,
    destination_sync_mode=DestinationSyncMode.overwrite,
)


TEST_CONFIGURED_CATALOG = ConfiguredAirbyteCatalog(streams=[TEST_CONFIGURED_AIRBYTE_STREAM_A, TEST_CONFIGURED_AIRBYTE_STREAM_B])


@pytest.mark.parametrize(
    "test_strictness_level, configured_catalog, states, missing_streams, expect_fail",
    [
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            [
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"airbytehq/integration-test": {"updated_at": "2121-06-30T10:22:10Z"}},
                        "stream_descriptor": {"name": "test_stream_a"},
                    },
                }
            ],
            [EmptyStreamConfiguration(name="test_stream_b", bypass_reason="no good reason")],
            False,
            id="High test strictness level, all missing streams are declared with bypass reason: does not fail.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            [
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"airbytehq/integration-test": {"updated_at": "2121-06-30T10:22:10Z"}},
                        "stream_descriptor": {"name": "test_stream_a"},
                    },
                }
            ],
            [EmptyStreamConfiguration(name="test_stream_b")],
            True,
            id="High test strictness level, missing streams are declared without bypass reason: fail.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            [
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"airbytehq/integration-test": {"updated_at": "2121-06-30T10:22:10Z"}},
                        "stream_descriptor": {"name": "test_stream_a"},
                    },
                }
            ],
            [EmptyStreamConfiguration(name="test_stream_b")],
            False,
            id="Low test strictness level, missing streams are declared without bypass reason: does fail.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            [
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"airbytehq/integration-test": {"updated_at": "2121-06-30T10:22:10Z"}},
                        "stream_descriptor": {"name": "test_stream_a"},
                    },
                }
            ],
            [],
            True,
            id="High test strictness level, missing streams are not declared: fail.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.low,
            TEST_CONFIGURED_CATALOG,
            [
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"airbytehq/integration-test": {"updated_at": "2121-06-30T10:22:10Z"}},
                        "stream_descriptor": {"name": "test_stream_a"},
                    },
                }
            ],
            [],
            False,
            id="Low test strictness level, missing streams are not declared: does not fail.",
        ),
    ],
)
def test_future_state_fixture(tmp_path, mocker, test_strictness_level, configured_catalog, states, missing_streams, expect_fail):
    mocker.patch.object(test_incremental.pytest, "fail")
    future_state_path = tmp_path / "abnormal_states.json"
    with open(future_state_path, "w") as f:
        json.dump(states, f)
    future_state_configuration = (future_state_path, missing_streams)
    output = future_state_fixture.__wrapped__(future_state_configuration, test_strictness_level, configured_catalog)
    assert output == states
    if expect_fail:
        test_incremental.pytest.fail.assert_called_once()
