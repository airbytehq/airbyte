# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from unittest import TestCase

import freezegun
from config_builder import ConfigBuilder
from conftest import generate_stream, mock_stream_api
from source_salesforce.api import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS

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
