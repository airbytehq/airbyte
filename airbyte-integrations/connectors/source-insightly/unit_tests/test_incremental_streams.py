#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timezone

from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator
from pytest import fixture
from source_insightly.source import IncrementalInsightlyStream

start_date = "2021-01-01T00:00:00Z"
authenticator = BasicHttpAuthenticator(username="test", password="")


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalInsightlyStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalInsightlyStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalInsightlyStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    # TODO: replace this with your expected cursor field
    expected_cursor_field = "DATE_UPDATED_UTC"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    inputs = {
        "current_stream_state": {"DATE_UPDATED_UTC": "2021-01-01T00:00:00Z"},
        "latest_record": {"DATE_UPDATED_UTC": "2021-02-01T00:00:00Z"},
    }
    expected_state = {"DATE_UPDATED_UTC": datetime(2021, 2, 1, 0, 0, 0, tzinfo=timezone.utc)}
    assert stream.get_updated_state(**inputs) == expected_state


def test_get_updated_state_no_current_state(patch_incremental_base_class):
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    inputs = {"current_stream_state": {}, "latest_record": {"DATE_UPDATED_UTC": "2021-01-01T00:00:00Z"}}
    expected_state = {"DATE_UPDATED_UTC": datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)}
    assert stream.get_updated_state(**inputs) == expected_state


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalInsightlyStream, "cursor_field", "dummy_field")
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
