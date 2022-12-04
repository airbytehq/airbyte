#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from source_my_hours.constants import REQUEST_HEADERS
from source_my_hours.stream import MyHoursStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(MyHoursStream, "path", "v0/example_endpoint")
    mocker.patch.object(MyHoursStream, "primary_key", "test_primary_key")
    mocker.patch.object(MyHoursStream, "__abstractmethods__", set())


def test_next_page_token(patch_base_class):
    stream = MyHoursStream()
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, requests_mock):
    stream = MyHoursStream()
    requests_mock.get("https://dummy", json=[{"name": "test"}])
    resp = requests.get("https://dummy")
    inputs = {"response": resp}
    expected_parsed_object = {"name": "test"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = MyHoursStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = REQUEST_HEADERS
    assert stream.request_headers(**inputs) == expected_headers
