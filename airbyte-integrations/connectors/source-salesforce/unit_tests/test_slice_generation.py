# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest import TestCase

import freezegun
import pytest
from config_builder import ConfigBuilder
from conftest import generate_stream, mock_stream_api
from source_salesforce.api import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS
from source_salesforce.streams import DEFAULT_LOOKBACK_SECONDS

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


_NOW = datetime.fromisoformat("2020-01-01T00:00:00+00:00")
_STREAM_NAME = UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS[0]


@freezegun.freeze_time(time_to_freeze=_NOW)
class IncrementalSliceGenerationTest(TestCase):
    """
    For this, we will be testing with UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS[0] as bulk stream slicing actually creates jobs. We will
    assume the bulk one usese the same logic.
    """

    def test_given_start_within_slice_range_when_stream_slices_then_return_one_slice_considering_10_minutes_lookback(self) -> None:
        config = ConfigBuilder().start_date(_NOW - timedelta(days=15)).stream_slice_step("P30D").build()
        stream = generate_stream(_STREAM_NAME, config, mock_stream_api(config))

        slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

        assert slices == [{"start_date": "2019-12-17T00:00:00.000+00:00", "end_date": "2020-01-01T00:00:00.000+00:00"}]

    def test_given_slice_range_smaller_than_now_minus_start_date_when_stream_slices_then_return_many_slices(self) -> None:
        config = ConfigBuilder().start_date(_NOW - timedelta(days=40)).stream_slice_step("P30D").build()
        stream = generate_stream(_STREAM_NAME, config, mock_stream_api(config))

        slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

        assert slices == [
            {"start_date": "2019-11-22T00:00:00.000+00:00", "end_date": "2019-12-22T00:00:00.000+00:00"},
            {"start_date": "2019-12-22T00:00:00.000+00:00", "end_date": "2020-01-01T00:00:00.000+00:00"},
        ]

    def test_given_end_date_when_stream_slices_then_cap_slices_at_end_date(self) -> None:
        config = ConfigBuilder().start_date(_NOW - timedelta(days=40)).end_date(_NOW - timedelta(days=5)).stream_slice_step("P30D").build()
        stream = generate_stream(_STREAM_NAME, config, mock_stream_api(config))

        slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

        assert slices == [
            {"start_date": "2019-11-22T00:00:00.000+00:00", "end_date": "2019-12-22T00:00:00.000+00:00"},
            {"start_date": "2019-12-22T00:00:00.000+00:00", "end_date": "2019-12-27T00:00:00.000+00:00"},
        ]

    def test_given_end_date_in_future_when_stream_slices_then_cap_slices_at_now(self) -> None:
        config = ConfigBuilder().start_date(_NOW - timedelta(days=40)).end_date(_NOW + timedelta(days=40)).stream_slice_step("P30D").build()
        stream = generate_stream(_STREAM_NAME, config, mock_stream_api(config))

        slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

        assert slices == [
            {"start_date": "2019-11-22T00:00:00.000+00:00", "end_date": "2019-12-22T00:00:00.000+00:00"},
            {"start_date": "2019-12-22T00:00:00.000+00:00", "end_date": "2020-01-01T00:00:00.000+00:00"},
        ]

    def test_given_end_date_not_after_start_date_when_generate_stream_then_raise_config_error(self) -> None:
        for end_date in [_NOW - timedelta(days=30), _NOW - timedelta(days=10)]:
            config = ConfigBuilder().start_date(_NOW - timedelta(days=10)).end_date(end_date).stream_slice_step("P30D").build()

            with pytest.raises(AirbyteTracedException, match="must be later than"):
                generate_stream(_STREAM_NAME, config, mock_stream_api(config))

    def test_given_state_and_end_date_when_stream_slices_then_cap_at_end_date(self) -> None:
        config = ConfigBuilder().start_date(_NOW - timedelta(days=60)).end_date(_NOW - timedelta(days=5)).stream_slice_step("P30D").build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"LastModifiedDate": "2019-12-12T00:00:00.000+00:00"}).build()
        stream = generate_stream(_STREAM_NAME, config, mock_stream_api(config), state=state)

        slices = list(stream.stream_slices(sync_mode=SyncMode.incremental))

        assert slices == [{"start_date": "2019-12-11T23:50:00.000+00:00", "end_date": "2019-12-27T00:00:00.000+00:00"}]

    def test_given_state_beyond_end_date_when_stream_slices_then_return_no_slices(self) -> None:
        config = ConfigBuilder().start_date(_NOW - timedelta(days=60)).end_date(_NOW - timedelta(days=30)).stream_slice_step("P30D").build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"LastModifiedDate": "2019-12-22T00:00:00.000+00:00"}).build()
        stream = generate_stream(_STREAM_NAME, config, mock_stream_api(config), state=state)

        assert list(stream.stream_slices(sync_mode=SyncMode.incremental)) == []


@freezegun.freeze_time(time_to_freeze=_NOW)
@pytest.mark.parametrize(
    "end_date_config, expected_last_slice_end",
    [
        pytest.param(None, "2020-01-01T00:00:00.000+00:00", id="omitted_end_date_uses_now"),
        pytest.param("", "2020-01-01T00:00:00.000+00:00", id="blank_end_date_uses_now"),
        pytest.param("2019-12-27", "2019-12-27T00:00:00.000+00:00", id="date_only_end_date"),
        pytest.param("2019-12-27T00:00:00Z", "2019-12-27T00:00:00.000+00:00", id="date_time_end_date"),
    ],
)
def test_end_date_formats(end_date_config: Optional[str], expected_last_slice_end: str) -> None:
    config = ConfigBuilder().start_date(_NOW - timedelta(days=40)).stream_slice_step("P30D").build()
    if end_date_config is not None:
        config["end_date"] = end_date_config
    stream = generate_stream(_STREAM_NAME, config, mock_stream_api(config))

    assert list(stream.stream_slices(sync_mode=SyncMode.full_refresh))[-1]["end_date"] == expected_last_slice_end


@freezegun.freeze_time(time_to_freeze=_NOW)
@pytest.mark.parametrize(
    "lookback_window_config, expected_lookback",
    [
        pytest.param(None, timedelta(seconds=DEFAULT_LOOKBACK_SECONDS), id="default_lookback_when_not_configured"),
        pytest.param("PT10M", timedelta(minutes=10), id="explicit_10_minutes"),
        pytest.param("PT30M", timedelta(minutes=30), id="30_minutes"),
        pytest.param("PT1H", timedelta(hours=1), id="1_hour"),
    ],
)
def test_lookback_window_applied_to_incremental_stream(
    lookback_window_config: Optional[str],
    expected_lookback: timedelta,
) -> None:
    config_builder = ConfigBuilder().start_date(_NOW - timedelta(days=15)).stream_slice_step("P30D")
    if lookback_window_config is not None:
        config_builder.lookback_window(lookback_window_config)
    config = config_builder.build()
    stream = generate_stream(_STREAM_NAME, config, mock_stream_api(config), legacy=False)

    assert stream._cursor._lookback_window == expected_lookback
