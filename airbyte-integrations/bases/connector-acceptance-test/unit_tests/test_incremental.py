#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import operator
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import Any, Optional
from unittest.mock import MagicMock, patch

import pytest
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateStats,
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
    descriptor: StreamDescriptor, stream_state: Optional[dict[str, Any]], data: Optional[dict[str, Any]] = None, source_stats: Optional[dict[str, Any]] = None
) -> AirbyteMessage:
    if data is None:
        data = stream_state
    if source_stats is None:
        source_stats = {"recordCount": 0.0}

    stream_state_blob = AirbyteStateBlob.parse_obj(stream_state) if stream_state else None
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(stream_descriptor=descriptor, stream_state=stream_state_blob),
            sourceStats=AirbyteStateStats(**source_stats),
            data=data
        ),
    )


@pytest.mark.parametrize("cursor_type", ["date", "string"])
@pytest.mark.parametrize(
    "records1, records2, latest_state, namespace, expected_error",
    [
        ([{"date": "2020-01-01"}, {"date": "2020-01-02"}], [], "2020-01-01", None, does_not_raise()),
        (
            [{"date": "2020-01-02"}, {"date": "2020-01-03"}],
            [],
            "2020-01-02",
            "public",
            does_not_raise(),
        ),
        (
            [{"date": "2020-01-02"}, {"date": "2020-01-03"}],
            [],
            "2020-01-02",
            None,
            does_not_raise(),
        ),
        (
            [{"date": "2020-01-01"}, {"date": "2020-01-02"}],
            [{"date": "2020-01-02"}, {"date": "2020-01-03"}],
            "2020-01-03",
            None,
            does_not_raise(),
        ),
        (
            [],
            [{"date": "2020-01-01"}],
            "2020-01-04",
            None,
            pytest.raises(AssertionError, match="First Read should produce at least one record"),
        ),
        (
            [{"date": "2020-01-01"}, {"date": "2020-01-02"}],
            [{"date": "2020-01-01"}, {"date": "2020-01-02"}],
            "2020-01-05",
            None,
            pytest.raises(AssertionError, match="Records should change between reads but did not."),
        ),
        (
            [{"date": "2020-01-02"}, {"date": "2020-01-03"}],
            [],
            "2020-01-06",
            None,
            does_not_raise(),
        ),
        (
            [{"date": "2020-01-01"}],
            [{"date": "2020-01-02"}],
            "2020-01-07",
            "public",
            does_not_raise(),
        ),
        (
            [{"date": "2020-01-01"}],
            [{"date": "2020-01-02"}],
            "someunparseablenonsensestate",
            None,
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
    mocker, records1, records2, latest_state, namespace, cursor_type, expected_error, run_per_stream_test
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
        stream_descriptor = StreamDescriptor(name="test_stream", namespace=namespace)
        call_read_output_messages = [
            *build_messages_from_record_data("test_stream", records1),
            build_per_stream_state_message(descriptor=stream_descriptor, stream_state={"date": latest_state}),
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
    "first_records, subsequent_records, inputs, expected_error",
    [
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 3.0}},
            ],
            [
                [],
            ],
            IncrementalConfig(),
            does_not_raise(),
            id="test_incremental_with_amount_of_states_less_than_3_whith_latest_only_state_checked",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 1.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-10"}, "sourceStats": {"recordCount": 2.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 3.0}},
            ],
            [
                # Read after 2022-05-08. The first state is expected to be skipped as empty. So, subsequent reads will start with the second state message.
                [
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-09"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-10"}, "sourceStats": {"recordCount": 2.0}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 3.0}},
                ],
                # Read after 2022-05-10. This is the second (last) subsequent read.
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-10"}, "sourceStats": {"recordCount": 2.0}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 3.0}},
                ]
            ],
            IncrementalConfig(),
            does_not_raise(),
            id="test_incremental_with_4_states_with_state_variation_checked",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-10"}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 0.0}},
            ],
            [
                []
            ],
            IncrementalConfig(),
            does_not_raise(),
            id="test_incremental_no_records_on_first_read_skips_stream",
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
                []
            ],
            IncrementalConfig(),
            does_not_raise(),
            id="test_incremental_no_states_on_first_read_skips_stream",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-13"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}, "sourceStats": {"recordCount": 2.0}},
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-13"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}, "sourceStats": {"recordCount": 2.0}},
                ],
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-13"}, "sourceStats": {"recordCount": 2.0}},
                ],
            ],
            IncrementalConfig(),
            does_not_raise(),
            id="test_first_incremental_only_younger_records",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-04"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-05"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-05"}, "sourceStats": {"recordCount": 2.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 3.0}},
            ],
            [
                [
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-04"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-05"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-05"}, "sourceStats": {"recordCount": 2.0}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-10"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-11"}},
                    {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-12"}},
                    {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 3.0}},
                ]
            ],
            IncrementalConfig(),
            pytest.raises(AssertionError, match="Records for subsequent reads with new state should be different"),
            id="test_incremental_returns_identical",
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-07"}},
                {"type": Type.RECORD, "name": "test_stream", "data": {"date": "2022-05-08"}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}},
            ],
            [
                [],
            ],
            IncrementalConfig(),
            does_not_raise(),
            id="test_incremental_with_empty_second_read",
        ),
    ],
)
async def test_per_stream_read_with_multiple_states(mocker, first_records, subsequent_records, inputs, expected_error):
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
            )
        ]
    )

    call_read_output_messages = [
        build_per_stream_state_message(
            descriptor=StreamDescriptor(name=record["name"]), stream_state=record["stream_state"], data=record.get("data", None), source_stats=record.get("sourceStats")
        )
        if record["type"] == Type.STATE
        else build_record_message(record["name"], record["data"])
        for record in list(first_records)
    ]
    call_read_with_state_output_messages = [
        [
            build_per_stream_state_message(
                descriptor=StreamDescriptor(name=record["name"]), stream_state=record["stream_state"], data=record.get("data", None), source_stats=record.get("sourceStats")
            )
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
            inputs=inputs,
        )


@pytest.mark.parametrize(
    "non_unique_states, expected_unique_states, expected_record_count_per_state",
    [
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}}
            ],
            [],
            [],
            id="combine_three_duplicates_into_a_single_state_message"
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 0.0}}
            ],
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}}
            ],
            [0.0],
            id="multiple_equal_states_with_different_sourceStats_considered_to_be_equal"
        ),
        pytest.param(
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 0.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-10"}, "sourceStats": {"recordCount": 7.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 3.0}}
            ],
            [
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-08"}, "sourceStats": {"recordCount": 2.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-10"}, "sourceStats": {"recordCount": 7.0}},
                {"type": Type.STATE, "name": "test_stream", "stream_state": {"date": "2022-05-12"}, "sourceStats": {"recordCount": 3.0}}
            ],
            [10.0, 3.0, 0.0]
        )
    ],
)
async def test_get_unique_state_messages(non_unique_states, expected_unique_states, expected_record_count_per_state):
    non_unique_states = [
        build_per_stream_state_message(
            descriptor=StreamDescriptor(name=state["name"]), stream_state=state["stream_state"], data=state.get("data", None), source_stats=state.get("sourceStats")
        )
        for state in non_unique_states
    ]
    expected_unique_states = [
        build_per_stream_state_message(
            descriptor=StreamDescriptor(name=state["name"]), stream_state=state["stream_state"], data=state.get("data", None), source_stats=state.get("sourceStats")
        )
        for state in expected_unique_states
    ]
    actual_unique_states = _TestIncremental()._get_unique_state_messages_with_record_count(non_unique_states)
    assert len(actual_unique_states) == len(expected_unique_states)

    if len(expected_unique_states):
        for actual_state_data, expected_state, expected_record_count in zip(actual_unique_states, expected_unique_states, expected_record_count_per_state):
            actual_state, actual_record_count = actual_state_data
            assert actual_state == expected_state
            assert actual_record_count == expected_record_count


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
