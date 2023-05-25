#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pendulum
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
    expected_cursor_field = "DATE_UPDATED_UTC"
    assert stream.cursor_field == expected_cursor_field


def test_incremental_params(patch_incremental_base_class):
    """
    After talking to the insightly team we learned that the DATE_UPDATED_UTC
    cursor is exclusive. Subtracting 1 second from the previous state makes it inclusive.
    """
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    inputs = {
        "stream_slice": None,
        "stream_state": {"DATE_UPDATED_UTC": pendulum.datetime(2023, 5, 15, 18, 12, 44, tz="UTC")},
        "next_page_token": None,
    }
    expected_params = {
        "count_total": True,
        "skip": 0,
        "top": 500,
        "updated_after_utc": "2023-05-15T18:12:43Z",  # 1 second subtracted from stream_state
    }
    assert stream.request_params(**inputs) == expected_params


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    inputs = {
        "current_stream_state": {"DATE_UPDATED_UTC": "2021-01-01T00:00:00Z"},
        "latest_record": {"DATE_UPDATED_UTC": "2021-02-01T00:00:00Z"},
    }
    expected_state = {"DATE_UPDATED_UTC": pendulum.datetime(2021, 2, 1, 0, 0, 0, tz="UTC")}
    assert stream.get_updated_state(**inputs) == expected_state


def test_get_updated_state_no_current_state(patch_incremental_base_class):
    stream = IncrementalInsightlyStream(authenticator=authenticator, start_date=start_date)
    inputs = {"current_stream_state": {}, "latest_record": {"DATE_UPDATED_UTC": "2021-01-01T00:00:00Z"}}
    expected_state = {"DATE_UPDATED_UTC": pendulum.datetime(2021, 1, 1, 0, 0, 0, tz="UTC")}
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
