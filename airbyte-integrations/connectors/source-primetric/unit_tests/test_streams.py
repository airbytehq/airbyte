#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_primetric.source import PrimetricStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PrimetricStream, "path", "v0/example_endpoint")
    mocker.patch.object(PrimetricStream, "primary_key", "test_primary_key")
    mocker.patch.object(PrimetricStream, "__abstractmethods__", set())


def test_request_headers(patch_base_class):
    stream = PrimetricStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = PrimetricStream()
    expected_method = "GET"
    assert stream.http_method == expected_method


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = PrimetricStream()
    expected_backoff_time = 31
    assert stream.backoff_time(response_mock) == expected_backoff_time
