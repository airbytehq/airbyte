#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone

import pytest
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import ConcurrencyCompatibleStateType
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    EpochValueConcurrentStreamStateConverter,
    IsoMillisConcurrentStreamStateConverter,
)


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
    "converter,start,state,expected_start",
    [
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            None,
            {},
            EpochValueConcurrentStreamStateConverter().zero_value,
            id="epoch-converter-no-state-no-start-start-is-zero-value",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            datetime.fromtimestamp(1617030403, timezone.utc),
            {},
            datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
            id="epoch-converter-no-state-with-start-start-is-start",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            None,
            {"created_at": 1617030404},
            datetime(2021, 3, 29, 15, 6, 44, tzinfo=timezone.utc),
            id="epoch-converter-state-without-start-start-is-from-state",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            datetime.fromtimestamp(1617030404, timezone.utc),
            {"created_at": 1617030403},
            datetime(2021, 3, 29, 15, 6, 44, tzinfo=timezone.utc),
            id="epoch-converter-state-before-start-start-is-start",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            datetime.fromtimestamp(1617030403, timezone.utc),
            {"created_at": 1617030404},
            datetime(2021, 3, 29, 15, 6, 44, tzinfo=timezone.utc),
            id="epoch-converter-state-after-start-start-is-from-state",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            None,
            {},
            IsoMillisConcurrentStreamStateConverter().zero_value,
            id="isomillis-converter-no-state-no-start-start-is-zero-value",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            {},
            datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            id="isomillis-converter-no-state-with-start-start-is-start",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            None,
            {"created_at": "2021-08-22T05:03:27.000Z"},
            datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            id="isomillis-converter-state-without-start-start-is-from-state",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            datetime(2022, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            {"created_at": "2021-08-22T05:03:27.000Z"},
            datetime(2022, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            id="isomillis-converter-state-before-start-start-is-start",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            datetime(2022, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            {"created_at": "2023-08-22T05:03:27.000Z"},
            datetime(2023, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            id="isomillis-converter-state-after-start-start-is-from-state",
        ),
    ],
)
def test_get_sync_start(converter, start, state, expected_start):
    assert converter._get_sync_start(CursorField("created_at"), state, start) == expected_start


@pytest.mark.parametrize(
    "converter, start, sequential_state, expected_output_state",
    [
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            datetime.fromtimestamp(0, timezone.utc),
            {},
            {
                "legacy": {},
                "slices": [
                    {
                        "start": EpochValueConcurrentStreamStateConverter().zero_value,
                        "end": EpochValueConcurrentStreamStateConverter().zero_value,
                    }
                ],
                "state_type": "date-range",
            },
            id="empty-input-state-epoch",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            datetime.fromtimestamp(1577836800, timezone.utc),
            {"created": 1617030403},
            {
                "state_type": "date-range",
                "slices": [
                    {
                        "start": datetime(2020, 1, 1, tzinfo=timezone.utc),
                        "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    }
                ],
                "legacy": {"created": 1617030403},
            },
            id="with-input-state-epoch",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            datetime(2020, 1, 1, tzinfo=timezone.utc),
            {"created": "2021-08-22T05:03:27.000Z"},
            {
                "state_type": "date-range",
                "slices": [
                    {
                        "start": datetime(2020, 1, 1, tzinfo=timezone.utc),
                        "end": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
                    }
                ],
                "legacy": {"created": "2021-08-22T05:03:27.000Z"},
            },
            id="with-input-state-isomillis",
        ),
    ],
)
def test_convert_from_sequential_state(converter, start, sequential_state, expected_output_state):
    comparison_format = "%Y-%m-%dT%H:%M:%S.%f"
    if expected_output_state["slices"]:
        _, conversion = converter.convert_from_sequential_state(CursorField("created"), sequential_state, start)
        assert conversion["state_type"] == expected_output_state["state_type"]
        assert conversion["legacy"] == expected_output_state["legacy"]
        for actual, expected in zip(conversion["slices"], expected_output_state["slices"]):
            assert actual["start"].strftime(comparison_format) == expected["start"].strftime(comparison_format)
            assert actual["end"].strftime(comparison_format) == expected["end"].strftime(comparison_format)
    else:
        _, conversion = converter.convert_from_sequential_state(CursorField("created"), sequential_state, start)
        assert conversion == expected_output_state


@pytest.mark.parametrize(
    "converter, concurrent_state, expected_output_state",
    [
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            {
                "state_type": "date-range",
                "slices": [
                    {
                        "start": datetime(1970, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    }
                ],
            },
            {"created": 172800},
            id="epoch-single-slice",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            {
                "state_type": "date-range",
                "slices": [
                    {
                        "start": datetime(1970, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    },
                    {
                        "start": datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2022, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    },
                ],
            },
            {"created": 172800},
            id="epoch-overlapping-slices",
        ),
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            {
                "state_type": "date-range",
                "slices": [
                    {
                        "start": datetime(1970, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    },
                    {
                        "start": datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2023, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    },
                ],
            },
            {"created": 172800},
            id="epoch-multiple-slices",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            {
                "state_type": "date-range",
                "slices": [
                    {
                        "start": datetime(1970, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    }
                ],
            },
            {"created": "1970-01-03T00:00:00.000Z"},
            id="isomillis-single-slice",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            {
                "state_type": "date-range",
                "slices": [
                    {
                        "start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    },
                    {
                        "start": datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2022, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    },
                ],
            },
            {"created": "1970-01-01T00:00:00.000Z"},
            id="isomillis-overlapping-slices",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            {
                "state_type": "date-range",
                "slices": [
                    {
                        "start": datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2021, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    },
                    {
                        "start": datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                        "end": datetime(2023, 3, 29, 15, 6, 43, tzinfo=timezone.utc),
                    },
                ],
            },
            {"created": "1970-01-01T00:00:00.000Z"},
            id="isomillis-multiple-slices",
        ),
    ],
)
def test_convert_to_sequential_state(converter, concurrent_state, expected_output_state):
    assert converter.convert_to_state_message(CursorField("created"), concurrent_state) == expected_output_state


@pytest.mark.parametrize(
    "converter, concurrent_state, expected_output_state",
    [
        pytest.param(
            EpochValueConcurrentStreamStateConverter(),
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": EpochValueConcurrentStreamStateConverter().zero_value,
            },
            {"created": 0},
            id="empty-slices-epoch",
        ),
        pytest.param(
            IsoMillisConcurrentStreamStateConverter(),
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "start": datetime(2021, 8, 22, 5, 3, 27, tzinfo=timezone.utc),
            },
            {"created": "2021-08-22T05:03:27.000Z"},
            id="empty-slices-isomillis",
        ),
    ],
)
def test_convert_to_sequential_state_no_slices_returns_legacy_state(converter, concurrent_state, expected_output_state):
    with pytest.raises(RuntimeError):
        converter.convert_to_state_message(CursorField("created"), concurrent_state)
