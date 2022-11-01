#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_nasa.source import NasaApod

config = {"api_key": "foobar"}


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(NasaApod, "path", "v0/example_endpoint")
    mocker.patch.object(NasaApod, "primary_key", "test_primary_key")
    mocker.patch.object(NasaApod, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = NasaApod(config=config)
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_stream_slices(patch_incremental_base_class):
    stream = NasaApod(config=config)
    start_date = datetime.now() - timedelta(days=3)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["date"], "stream_state": {"date": start_date.strftime("%Y-%m-%d")}}
    expected_stream_slice = [{"date": (start_date + timedelta(days=x)).strftime("%Y-%m-%d")} for x in range(4)]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(NasaApod, "cursor_field", "dummy_field")
    stream = NasaApod(config=config)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = NasaApod(config=config)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = NasaApod(config=config)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
