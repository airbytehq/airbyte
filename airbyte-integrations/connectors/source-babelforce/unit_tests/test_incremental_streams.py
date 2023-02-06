#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dateutil.parser import parse
from dateutil.tz import tzutc
from pytest import fixture
from source_babelforce.source import DEFAULT_CURSOR, IncrementalBabelforceStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalBabelforceStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalBabelforceStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalBabelforceStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalBabelforceStream(region="services")
    expected_cursor_field = DEFAULT_CURSOR
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalBabelforceStream(region="services")
    fake_date = "2022-02-01T00:00:00"
    inputs = {"current_stream_state": None, "latest_record": {DEFAULT_CURSOR: fake_date}}
    expected_state = {DEFAULT_CURSOR: parse(fake_date).replace(tzinfo=tzutc()).isoformat(timespec="seconds")}
    assert stream.get_updated_state(**inputs) == expected_state


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalBabelforceStream, "cursor_field", "dummy_field")
    stream = IncrementalBabelforceStream(region="services")
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalBabelforceStream(region="services")
    assert stream.source_defined_cursor
