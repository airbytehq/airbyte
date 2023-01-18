#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from source_clockify.streams import ClockifyStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(ClockifyStream, "path", "v0/example_endpoint")
    mocker.patch.object(ClockifyStream, "primary_key", "test_primary_key")
    mocker.patch.object(ClockifyStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = ClockifyStream(workspace_id=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"page-size": 50}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = ClockifyStream(workspace_id=MagicMock())
    inputs = {"response": MagicMock()}
    expected_token = {"page": 2}
    assert stream.next_page_token(**inputs) == expected_token


def test_read_records(patch_base_class):
    stream = ClockifyStream(workspace_id=MagicMock())
    assert stream.read_records(sync_mode=SyncMode.full_refresh)


def test_request_headers(patch_base_class):
    stream = ClockifyStream(workspace_id=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = ClockifyStream(workspace_id=MagicMock())
    expected_method = "GET"
    assert stream.http_method == expected_method
