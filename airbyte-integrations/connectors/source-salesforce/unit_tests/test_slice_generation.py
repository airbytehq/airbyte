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
