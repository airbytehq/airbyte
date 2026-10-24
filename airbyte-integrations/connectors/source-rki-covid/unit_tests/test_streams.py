#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_rki_covid.source import RkiCovidStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(RkiCovidStream, "path", "v0/example_endpoint")
    mocker.patch.object(RkiCovidStream, "primary_key", "test_primary_key")
    mocker.patch.object(RkiCovidStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = RkiCovidStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = RkiCovidStream()
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_request_headers(patch_base_class):
    stream = RkiCovidStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = RkiCovidStream()
    expected_method = "GET"
    assert stream.http_method == expected_method
