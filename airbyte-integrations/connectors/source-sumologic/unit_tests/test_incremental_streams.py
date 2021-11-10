#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import copy

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_sumologic.source import IncrementalSumologicStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalSumologicStream, "__abstractmethods__", set())


@fixture
def client(mocker):
    yield mocker.Mock()


@fixture
def config(mocker):
    yield {
        "access_id": "foo",
        "access_key": "bar",
        "query": "xyz",
    }


def test_cursor_field(patch_incremental_base_class, client, config):
    stream = IncrementalSumologicStream(client, config)
    assert stream.cursor_field == "_receipttime"


def test_cursor_field__when_by_receipt_time(patch_incremental_base_class, client, config):
    config_ = copy.deepcopy(config)
    config_["by_receipt_time"] = True
    stream = IncrementalSumologicStream(client, config_)
    assert stream.cursor_field == "_receipttime"


def test_get_updated_state(patch_incremental_base_class, client, config):
    stream = IncrementalSumologicStream(client, config)
    inputs = {"current_stream_state": {"_receipttime": "1633060800000"}, "latest_record": {"_receipttime": "1633147200000"}}
    expected_state = {"_receipttime": "1633147200000"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, client, config):
    stream = IncrementalSumologicStream(client, config)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker, client, config):
    mocker.patch.object(IncrementalSumologicStream, "cursor_field", "dummy_field")
    stream = IncrementalSumologicStream(client, config)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, client, config):
    stream = IncrementalSumologicStream(client, config)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class, client, config):
    stream = IncrementalSumologicStream(client, config)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
