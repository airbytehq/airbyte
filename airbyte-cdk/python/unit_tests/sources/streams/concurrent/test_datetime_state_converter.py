#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone

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
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import ConcurrencyCompatibleStateType
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    EpochValueConcurrentStreamStateConverter,
    IsoMillisConcurrentStreamStateConverter,
)


@pytest.mark.parametrize(
    "converter, stream, start, input_state, expected_output_state",
    [
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            None,
            [],
            {
                "legacy": {},
                "slices": [],
                "state_type": "date-range",
                "low_water_mark": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            },
            id="no-start-no-input-state-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            5,
            [],
            {
                "legacy": {},
                "slices": [],
                "state_type": "date-range",
                "low_water_mark": datetime(1970, 1, 1, 0, 0, 5, tzinfo=timezone.utc),
                "start": datetime(1970, 1, 1, 0, 0, 5, tzinfo=timezone.utc),
            },
            id="with-start-no-input-state-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            None,
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": 1703020837}),
                    ),
                ),
            ],
            {
                "legacy": {"created_at": 1703020837},
                "slices": [{"end": datetime(2023, 12, 19, 21, 20, 37, tzinfo=timezone.utc),
                            "start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)}],
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(2023, 12, 19, 21, 20, 37, tzinfo=timezone.utc)
            },
            id="incompatible-no-start-input-state-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            1671484837,
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": 1703020837}),
                    ),
                ),
            ],
            {
                "legacy": {"created_at": 1703020837},
                "slices": [{"end": datetime(2023, 12, 19, 21, 20, 37, tzinfo=timezone.utc),
                            "start": datetime(2022, 12, 19, 21, 20, 37, tzinfo=timezone.utc)}],
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2022, 12, 19, 21, 20, 37, tzinfo=timezone.utc),
                "low_water_mark": datetime(2023, 12, 19, 21, 20, 37, tzinfo=timezone.utc)
            },
            id="incompatible-with-start-before-last-state-input-state-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            1734643237,
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": 1703020837}),
                    ),
                ),
            ],
            {
                "legacy": {"created_at": 1703020837},
                "slices": [{"end": datetime(2024, 12, 19, 21, 20, 37, tzinfo=timezone.utc),
                            "start": datetime(2024, 12, 19, 21, 20, 37, tzinfo=timezone.utc)}],
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2024, 12, 19, 21, 20, 37, tzinfo=timezone.utc),
                "low_water_mark": datetime(2024, 12, 19, 21, 20, 37, tzinfo=timezone.utc)
            },
            id="incompatible-with-start-after-last-state-input-state-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            5,
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj(
                            {
                                "created_at": 1703020837,
                                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                            },
                        ),
                    ),
                ),
            ],
            {
                "created_at": 1703020837,
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(1970, 1, 1, 0, 0, 5, tzinfo=timezone.utc),
            },
            id="compatible-input-state-epoch",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            None,
            [],
            {
                "legacy": {},
                "slices": [],
                "state_type": "date-range",
                "start": datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            },
            id="no-start-no-input-state-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            "0002-01-01T00:00:00.000Z",
            [],
            {
                "legacy": {},
                "slices": [],
                "state_type": "date-range",
                "start": datetime(2, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(2, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            },
            id="with-start-no-input-state-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            None,
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": "2021-01-18T21:18:20.000Z"}),
                    ),
                ),
            ],
            {
                "legacy": {"created_at": "2021-01-18T21:18:20.000Z"},
                "slices": [{"end": datetime(2021, 1, 18, 21, 18, 20, tzinfo=timezone.utc),
                            "start": datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)}],
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 1, 18, 21, 18, 20, tzinfo=timezone.utc),
            },
            id="incompatible-no-start-input-state-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            "0002-01-01T00:00:00.000Z",
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": "2021-01-18T21:18:20.000Z"}),
                    ),
                ),
            ],
            {
                "legacy": {"created_at": "2021-01-18T21:18:20.000Z"},
                "slices": [{"end": datetime(2021, 1, 18, 21, 18, 20, tzinfo=timezone.utc),
                            "start": datetime(2, 1, 1, 0, 0, 0, tzinfo=timezone.utc)}],
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 1, 18, 21, 18, 20, tzinfo=timezone.utc),
            },
            id="incompatible-with-start-before-last-input-state-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            "2022-01-18T21:18:20.000Z",
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": "2021-01-18T21:18:20.000Z"}),
                    ),
                ),
            ],
            {
                "legacy": {"created_at": "2021-01-18T21:18:20.000Z"},
                "slices": [{"end": datetime(2022, 1, 18, 21, 18, 20, tzinfo=timezone.utc),
                            "start": datetime(2022, 1, 18, 21, 18, 20, tzinfo=timezone.utc)}],
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2022, 1, 18, 21, 18, 20, tzinfo=timezone.utc),
                "low_water_mark": datetime(2022, 1, 18, 21, 18, 20, tzinfo=timezone.utc),
            },
            id="incompatible-with-start-after-last-input-state-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            None,
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="stream1", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj(
                            {
                                "created_at": "2021-01-18T21:18:20.000Z",
                                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                            },
                        ),
                    ),
                ),
            ],
            {
                "created_at": "2021-01-18T21:18:20.000Z",
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            },
            id="compatible-input-state-isomillis",
        ),
    ],
)
def test_concurrent_connector_state_manager_get_stream_state(converter, stream, start, input_state, expected_output_state):
    state_manager = ConnectorStateManager({"stream1": stream}, input_state)
    concurrent_state = converter.get_concurrent_stream_state(
        CursorField("created_at"),
        start,
        state_manager.get_stream_state("stream1", None)
    )
    assert concurrent_state == expected_output_state


@pytest.mark.parametrize(
    "converter, input_state, is_compatible",
    [
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            {"state_type": "date-range"},
            True,
            id="no-input-state-is-compatible-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            {
                "created_at": "2022_05_22",
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
            },
            True,
            id="input-state-with-date_range-is-compatible-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            {
                "created_at": "2022_05_22",
                "state_type": "fake",
            },
            False,
            id="input-state-with-fake-state-type-is-not-compatible-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            {
                "created_at": "2022_05_22",
            },
            False,
            id="input-state-without-state_type-is-not-compatible-epoch",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            {"state_type": "date-range"},
            True,
            id="no-input-state-is-compatible-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            {
                "created_at": "2022_05_22",
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
            },
            True,
            id="input-state-with-date_range-is-compatible-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            {
                "created_at": "2022_05_22",
                "state_type": "fake",
            },
            False,
            id="input-state-with-fake-state-type-is-not-compatible-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            {
                "created_at": "2022_05_22",
            },
            False,
            id="input-state-without-state_type-is-not-compatible-isomillis",
        ),
    ],
)
def test_concurrent_stream_state_converter_is_state_message_compatible(converter, input_state, is_compatible):
    assert converter.is_state_message_compatible(input_state) == is_compatible


@pytest.mark.parametrize(
    "converter, stream, start, sequential_state, expected_output_state",
    [
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            0,
            {},
            {
                "legacy": {},
                "slices": [],
                "state_type": "date-range",
                "start": EpochValueConcurrentStreamStateConverter().zero_value,
                "low_water_mark": EpochValueConcurrentStreamStateConverter().zero_value,
            },
            id="empty-input-state-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            1617030403,
            {"created": 1617030403},
            {
                "state_type": "date-range",
                "slices": [{"start": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                            "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc)}],
                "legacy": {"created": 1617030403},
                "start": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
            },
            id="with-input-state-epoch",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            None,
            {},
            {
                "legacy": {},
                "slices": [],
                "state_type": "date-range",
                "start": IsoMillisConcurrentStreamStateConverter().zero_value,
                "low_water_mark": IsoMillisConcurrentStreamStateConverter().zero_value,
            },
            id="empty-input-state-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            "2020-01-01T00:00:00.000Z",
            {"created": "2021-08-22T05:03:27.000Z"},
            {
                "state_type": "date-range",
                "slices": [{"start": datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                            "end": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc)}],
                "legacy": {"created": "2021-08-22T05:03:27.000Z"},
                "start": datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            },
            id="with-input-state-isomillis",
        ),
    ],
)
def test_convert_from_sequential_state(converter, stream, start, sequential_state, expected_output_state):
    comparison_format = "%Y-%m-%dT%H:%M:%S.%f"
    if expected_output_state["slices"]:
        conversion = converter.convert_from_sequential_state(CursorField("created"), start, sequential_state)
        assert conversion["state_type"] == expected_output_state["state_type"]
        assert conversion["legacy"] == expected_output_state["legacy"]
        assert conversion["start"] == expected_output_state["start"]
        for actual, expected in zip(conversion["slices"], expected_output_state["slices"]):
            assert actual["start"].strftime(comparison_format) == expected["start"].strftime(comparison_format)
            assert actual["end"].strftime(comparison_format) == expected["end"].strftime(comparison_format)
    else:
        assert converter.convert_from_sequential_state(CursorField("created"), start, sequential_state) == expected_output_state


@pytest.mark.parametrize(
    "converter, stream, concurrent_state, expected_output_state",
    [
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": EpochValueConcurrentStreamStateConverter().zero_value,
                "low_water_mark": EpochValueConcurrentStreamStateConverter().zero_value,
            },
            {"created": 0},
            id="empty-slices-epoch-same-start-and-low-water-mark-no-slices",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                "low_water_mark": datetime(2020, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
            },
            {"created": 1585494403},
            id="empty-slices-epoch-low-water-mark-before-start",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2020, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
            },
            {"created": 1617030403},
            id="empty-slices-epoch-low-water-mark-after-start",  # The sync advanced in the past, but no new records were found this sync
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": "date-range",
                "slices": [{"start": datetime(1970, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                            "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc)}],
                "start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(1970, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
            },
            {"created": 86400},
            id="with-slices-epoch-low-water-mark-before-slice",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": "date-range",
                "slices": [{"start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                            "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc)}],
                "start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(1970, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
            },
            {"created": 1617030403},
            id="with-slices-epoch-low-water-mark-middle-of-slice",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": "date-range",
                "slices": [{"start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                            "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc)}],
                "start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 4, 29, 15, 6, 43, tzinfo=timezone.utc)
            },
            {"created": 1619708803},
            id="with-slices-epoch-low-water-mark-after-slice",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            },
            {"created": "2021-08-22T05:03:27.000Z"},
            id="empty-slices-isomillis",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
                "low_water_mark": datetime(2022, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            },
            {"created": "2022-08-22T05:03:27.000Z"},
            id="empty-slices-isomillis-low-water-mark-after-start",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": "date-range",
                "slices": [{"start": datetime(1, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                            "end": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc)}],
                "start": datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "low_water_mark": datetime(1, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
            },
            {"created": "0001-01-02T00:00:00.000Z"},
            id="with-slices-isomillis-low-water-mark-before-slice",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": "date-range",
                "slices": [{"start": datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                            "end": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc)}],
                "start": datetime(2021, 7, 1, 5, 3, 27, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 7, 22, 5, 3, 27, tzinfo=timezone.utc)
            },
            {"created": "2021-08-22T05:03:27.000Z"},
            id="with-slices-isomillis-low-water-mark-middle-of-slice",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            {
                "state_type": "date-range",
                "slices": [{"start": datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                            "end": datetime(2021, 7, 22, 5, 3, 27, tzinfo=timezone.utc)}],
                "start": datetime(2020, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
                "low_water_mark": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            },
            {"created": "2021-08-22T05:03:27.000Z"},
            id="with-slices-isomillis-low-water-mark-after-slice",
        ),
    ],
)
def test_convert_to_sequential_state(converter, stream, concurrent_state, expected_output_state):
    assert converter.convert_to_sequential_state(CursorField("created"), concurrent_state) == expected_output_state
