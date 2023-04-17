#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from unittest.mock import MagicMock

from pytest import fixture
from source_criteo.streams import CriteoStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(CriteoStream, "path", "2023-01/statistics/report")
    mocker.patch.object(CriteoStream, "primary_key", "test_primary_key")
    mocker.patch.object(CriteoStream, "__abstractmethods__", set())

    return {
        "config": {
            "advertiserIds": "10817,10398",
            "start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
            "end_date": datetime.datetime.strftime((datetime.datetime.now()), "%Y-%m-%d"),
            "dimensions": ["AdvertiserId", "Os", "Day"],
            "metrics": ["Displays", "Clicks"],
            "currency": "EUR",
            "timezone": "Europe/Rome",
            "lookback_window": 1,
        }
    }


def test_cursor_field(patch_incremental_base_class):
    stream = CriteoStream(authenticator=MagicMock(), **patch_incremental_base_class["config"])
    expected_cursor_field = "Day"
    assert stream.cursor_field == expected_cursor_field


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(CriteoStream, "cursor_field", "dummy_field")
    stream = CriteoStream(authenticator=MagicMock(), **patch_incremental_base_class["config"])
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = CriteoStream(authenticator=MagicMock(), **patch_incremental_base_class["config"])
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = CriteoStream(authenticator=MagicMock(), **patch_incremental_base_class["config"])
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
