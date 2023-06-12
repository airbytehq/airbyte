#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_doubleverify.source import DoubleverifyStream
import gzip
import requests

@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(DoubleverifyStream, "path", "v0/example_endpoint")
    mocker.patch.object(DoubleverifyStream, "primary_key", "test_primary_key")
    mocker.patch.object(DoubleverifyStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    config_mock = MagicMock()
    config_catalog = './integration_tests/configured_catalog.json'
    stream = DoubleverifyStream(config=config_mock, catalog_stream=config_catalog)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    config_mock = MagicMock()
    config_catalog = './integration_tests/configured_catalog.json'
    stream = DoubleverifyStream(config=config_mock, catalog_stream=config_catalog)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    config_mock = MagicMock()
    config_catalog = './integration_tests/configured_catalog.json'
    stream = DoubleverifyStream(config=config_mock, catalog_stream=config_catalog)
    with open('unit_tests/mock_response.csv', 'rb') as file:
        mock_response = gzip.compress(file.read())

    response = requests.Response()
    response.status_code = 200
    response.headers['Content-Type'] = 'application/json'
    response.headers['Accept'] = 'text/csv'
    response.headers['Accept-Encoding'] = 'gzip'
    response.encoding = 'utf-8'
    response._content = mock_response
    
    inputs = {"response": response}

    expected_parsed_object = {
        'ad_server_campaign_code': '',
        'brand_suitable_ads': '1',
        'campaign': '',
        'date': '2023-01-01',
        'monitored_ads': '1',
        'uc_blocks': '0',
        'uc_incidents': '0'
    }
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    config_mock = MagicMock()
    config_catalog = './integration_tests/configured_catalog.json'
    stream = DoubleverifyStream(config=config_mock, catalog_stream=config_catalog)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {
        'Accept': 'text/csv',
        'Accept-Encoding': 'gzip',
        'Authorization': "Bearer "+"{}".format(config_mock.get("access_token")),
        'Content-Type': 'application/json'
    }
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    config_mock = MagicMock()
    config_catalog = './integration_tests/configured_catalog.json'
    stream = DoubleverifyStream(config=config_mock, catalog_stream=config_catalog)
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    config_mock = MagicMock()
    config_catalog = './integration_tests/configured_catalog.json'
    stream = DoubleverifyStream(config=config_mock, catalog_stream=config_catalog)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    config_mock = MagicMock()
    config_catalog = './integration_tests/configured_catalog.json'
    stream = DoubleverifyStream(config=config_mock, catalog_stream=config_catalog)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
