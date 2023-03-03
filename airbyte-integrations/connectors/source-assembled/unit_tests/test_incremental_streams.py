#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
from airbyte_cdk.models import SyncMode
from freezegun import freeze_time
from pytest import fixture
from source_assembled.source import IncrementalAssembledStream

default_start_date = pendulum.now().subtract(days=7).replace(hour=0, minute=0, second=0, microsecond=0)

kwargs = {
    "default_start_date": default_start_date,
    "history_days": 30,
    "future_days": 30,
}


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalAssembledStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalAssembledStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalAssembledStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalAssembledStream(**kwargs)
    expected_cursor_field = "start_time"
    assert stream.cursor_field == expected_cursor_field


@freeze_time("2022-02-05")
def test_stream_slices_no_state(patch_incremental_base_class):
    kwargs["default_start_date"] = pendulum.parse("2022-02-01")
    stream = IncrementalAssembledStream(**kwargs)

    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "start_time"}
    expected_stream_slice = {"end_time": 1643760000, "start_time": 1643673600}
    assert next(stream.stream_slices(**inputs)) == expected_stream_slice


@freeze_time("2022-02-05")
def test_stream_slices_state(patch_incremental_base_class):
    kwargs["default_start_date"] = pendulum.parse("2022-02-01")
    stream = IncrementalAssembledStream(**kwargs)

    start_dt = pendulum.parse("2022-02-04")

    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "start_time", "stream_state": {"start_time": start_dt.int_timestamp}}

    # should be 30 days back from 2022-02-04
    expected_stream_slice = {"end_time": 1641513600, "start_time": 1641427200}
    assert next(stream.stream_slices(**inputs)) == expected_stream_slice


@freeze_time("2022-02-05")
def test_stream_slices_state_same_day(patch_incremental_base_class):
    kwargs["default_start_date"] = pendulum.parse("2022-02-01")
    stream = IncrementalAssembledStream(**kwargs)

    start_dt = pendulum.parse("2022-02-05")

    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "start_time", "stream_state": {"start_time": start_dt.int_timestamp}}

    # should be previous day only
    expected_stream_slice = {"end_time": 1644019200, "start_time": 1643932800}
    slices = list(stream.stream_slices(**inputs))
    assert len(slices) == 1
    assert slices[0] == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalAssembledStream, "cursor_field", "dummy_field")
    stream = IncrementalAssembledStream(**kwargs)

    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalAssembledStream(**kwargs)

    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalAssembledStream(**kwargs)

    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
