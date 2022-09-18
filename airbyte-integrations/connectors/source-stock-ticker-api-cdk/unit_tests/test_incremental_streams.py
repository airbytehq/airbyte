#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime

import pytest
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_stock_ticker_api_cdk.source import Prices


@pytest.fixture(name="config")
def config_fixture():
    config = {'api_key': 'api_key', 'stock_ticker': 'stock_ticker'}
    return config


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(Prices, "path", "v0/example_endpoint")
    mocker.patch.object(Prices, "primary_key", "test_primary_key")
    mocker.patch.object(Prices, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = Prices({'api_key': 'api_key', 'stock_ticker': 'stock_ticker'})
    expected_cursor_field = 'date'
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, config):
    stream = Prices(config)
    inputs = {"current_stream_state": None, "latest_record": None}
    expected_state = {}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, config):
    stream = Prices(config)
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {"date": now}}
    expected_stream_slice = [{'date': now}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker, config):
    mocker.patch.object(Prices, "cursor_field", "dummy_field")
    stream = Prices(config)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, config):
    stream = Prices(config)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class, config):
    stream = Prices(config)
    expected_checkpoint_interval = 3
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
