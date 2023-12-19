#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping

import pytest
from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    StreamDescriptor,
    SyncMode,
)
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.streams.concurrent.state_converter import (
    ConcurrencyCompatibleStateType,
    ConcurrentStreamStateConverter,
    EpochValueConcurrentStreamStateConverter,
)


class MockConcurrentConnectorStateConverter(ConcurrentStreamStateConverter):
    def convert_from_sequential_state(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        state["state_type"] = ConcurrencyCompatibleStateType.date_range.value
        return state

    def convert_to_sequential_state(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        state.pop("state_type")
        return state

    @staticmethod
    def increment(timestamp: Any) -> Any:
        return timestamp + 1


@pytest.mark.parametrize(
    "stream, input_state, expected_output_state",
    [
        pytest.param(
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            [],
            {"state_type": ConcurrencyCompatibleStateType.date_range.value},
            id="no-input-state",
        ),
        pytest.param(
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": "2022_05_22"}),
                    ),
                ),
            ],
            {"created_at": "2022_05_22", "state_type": ConcurrencyCompatibleStateType.date_range.value},
            id="incompatible-input-state",
        ),
        pytest.param(
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj(
                            {
                                "created_at": "2022_05_22",
                                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                            },
                        ),
                    ),
                ),
            ],
            {"created_at": "2022_05_22", "state_type": ConcurrencyCompatibleStateType.date_range.value},
            id="compatible-input-state",
        ),
    ],
)
def test_concurrent_connector_state_manager_get_stream_state(stream, input_state, expected_output_state):
    state_manager = ConnectorStateManager({"stream1": stream}, input_state)
    state_converter = MockConcurrentConnectorStateConverter()
    assert state_converter.get_concurrent_stream_state(state_manager.get_stream_state("stream1", None)) == expected_output_state


@pytest.mark.parametrize(
    "input_state, is_compatible",
    [
        pytest.param(
            {},
            False,
            id="no-input-state-is-not-compatible",
        ),
        pytest.param(
            {
                "created_at": "2022_05_22",
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
            },
            True,
            id="input-state-with-date_range-is-compatible",
        ),
        pytest.param(
            {
                "created_at": "2022_05_22",
                "state_type": "fake",
            },
            False,
            id="input-state-with-fake-state-type-is-not-compatible",
        ),
        pytest.param(
            {
                "created_at": "2022_05_22",
            },
            False,
            id="input-state-without-state_type-is-not-compatible",
        ),
    ],
)
def test_concurrent_stream_state_converter_is_state_message_compatible(input_state, is_compatible):
    assert ConcurrentStreamStateConverter.is_state_message_compatible(input_state) == is_compatible


@pytest.mark.parametrize(
    "input_intervals, expected_merged_intervals",
    [
        pytest.param(
            [],
            [],
            id="no-intervals",
        ),
        pytest.param(
            [{"start": 0, "end": 1}],
            [{"start": 0, "end": 1}],
            id="single-interval",
        ),
        pytest.param(
            [{"start": 0, "end": 1}, {"start": 0, "end": 1}],
            [{"start": 0, "end": 1}],
            id="duplicate-intervals",
        ),
        pytest.param(
            [{"start": 0, "end": 1}, {"start": 0, "end": 2}],
            [{"start": 0, "end": 2}],
            id="overlapping-intervals",
        ),
        pytest.param(
            [{"start": 0, "end": 3}, {"start": 1, "end": 2}],
            [{"start": 0, "end": 3}],
            id="enclosed-intervals",
        ),
        pytest.param(
            [{"start": 1, "end": 2}, {"start": 0, "end": 1}],
            [{"start": 0, "end": 2}],
            id="unordered-intervals",
        ),
        pytest.param(
            [{"start": 0, "end": 1}, {"start": 2, "end": 3}],
            [{"start": 0, "end": 3}],
            id="adjacent-intervals",
        ),
        pytest.param(
            [{"start": 3, "end": 4}, {"start": 0, "end": 1}],
            [{"start": 0, "end": 1}, {"start": 3, "end": 4}],
            id="nonoverlapping-intervals",
        ),
        pytest.param(
            [{"start": 0, "end": 1}, {"start": 2, "end": 3}, {"start": 10, "end": 11}, {"start": 1, "end": 4}],
            [{"start": 0, "end": 4}, {"start": 10, "end": 11}],
            id="overlapping-and-nonoverlapping-intervals",
        ),
    ],
)
def test_concurrent_stream_state_converter_merge_intervals(input_intervals, expected_merged_intervals):
    return MockConcurrentConnectorStateConverter.merge_intervals(input_intervals) == expected_merged_intervals


@pytest.mark.parametrize(
    "stream, sequential_state, expected_output_state",
    [
        pytest.param(
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {},
            {"slices": [], "state_type": ConcurrencyCompatibleStateType.date_range.value, "legacy": {}},
            id="empty-input-state",
        ),
        pytest.param(
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {"created": 1617030403},
            {
                "state_type": "date-range",
                "slices": [{"start": 0, "end": 1617030403}],
                "legacy": {"created": 1617030403},
            },
            id="with-input-state",
        ),
    ],
)
def test_epoch_state_converter_convert_from_sequential_state(stream, sequential_state, expected_output_state):
    state_manager = EpochValueConcurrentStreamStateConverter("created")
    assert state_manager.convert_from_sequential_state(sequential_state) == expected_output_state


@pytest.mark.parametrize(
    "stream, concurrent_state, expected_output_state",
    [
        pytest.param(
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {"state_type": ConcurrencyCompatibleStateType.date_range.value},
            {},
            id="empty-input-state",
        ),
        pytest.param(
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {"state_type": "date-range", "slices": [{"start": 0, "end": 1617030403}]},
            {"created": 1617030403},
            id="with-input-state",
        ),
    ],
)
def test_epoch_state_converter_convert_to_sequential_state(stream, concurrent_state, expected_output_state):
    state_manager = EpochValueConcurrentStreamStateConverter("created")
    assert state_manager.convert_to_sequential_state(concurrent_state) == expected_output_state
