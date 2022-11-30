#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_pinterest.source import AdAccountAnalytics, Campaigns, IncrementalPinterestSubStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalPinterestSubStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalPinterestSubStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalPinterestSubStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    expected_cursor_field = "updated_time"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, test_current_stream_state):
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    inputs = {"current_stream_state": test_current_stream_state, "latest_record": test_current_stream_state}
    expected_state = {"updated_time": "2021-10-22"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, test_current_stream_state, test_incremental_config):
    stream = IncrementalPinterestSubStream(None, config=test_incremental_config)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "updated_time", "stream_state": test_current_stream_state}
    expected_stream_slice = {"start_date": "2021-10-22", "end_date": "2021-11-21"}
    assert next(stream.stream_slices(**inputs)) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalPinterestSubStream, "cursor_field", "dummy_field")
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_request_params(patch_incremental_base_class):
    stream = AdAccountAnalytics(None, config=MagicMock())
    test_slice = {"start_date": "2022-01-01", "end_date": "2022-01-02"}
    expected_property = "columns"
    res = stream.request_params({}, test_slice)
    assert expected_property in res


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, False),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_incremental_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = AdAccountAnalytics(None, config=MagicMock())
    assert stream.should_retry(response_mock) == should_retry


def test_parse_response(patch_incremental_base_class, test_response_filter, test_current_stream_state):
    stream = Campaigns(None, config=MagicMock())
    expected_parsed_object = [{"updated_time": "2021-11-01"}]
    result = list(stream.parse_response(test_response_filter, test_current_stream_state))
    assert result == expected_parsed_object
