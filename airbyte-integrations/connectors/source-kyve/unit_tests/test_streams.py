#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests

from source_kyve.source import KYVEStream as KyveStream
from . import config, pool_data
from .test_data import MOCK_RESPONSE_BINARY

@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(KyveStream, "path", "v0/example_endpoint")
    mocker.patch.object(KyveStream, "primary_key", "test_primary_key")
    mocker.patch.object(KyveStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = KyveStream(config, pool_data)
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": {}, "next_page_token": None}
    # TODO: replace this with your expected request parameters
    expected_params = {'pagination.limit': 100, 'pagination.offset': 0}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = KyveStream(config, pool_data)
    # TODO: replace this with your input parameters
    inputs = {"response": MagicMock()}
    # TODO: replace this with your expected next page token
    expected_token = {'pagination.offset': 100}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, monkeypatch):
    stream = KyveStream(config, pool_data)

    input_request = requests.Response()
    inputs = {"response": input_request, "stream_state": {}}

    mock_input_request_response_json = {'finalized_bundles': [{"storage_id": 10}], 'pagination': {'next_key': None, 'total': '0'}}

    mock_finalized_bundles_request = MagicMock(return_value=mock_input_request_response_json)
    monkeypatch.setattr('requests.Response.json', mock_finalized_bundles_request)

    class _MockContentResponse:
        def __init__(self):
            self.content = MOCK_RESPONSE_BINARY
    mock_get_content = MagicMock(return_value=_MockContentResponse())
    monkeypatch.setattr('requests.get', mock_get_content)
    mock_response_ok = MagicMock(return_value=True)
    monkeypatch.setattr('requests.Response.ok', mock_response_ok)

    expected_parsed_object = {
        'key': '10647520',
        'value': {
            'hash': '0x3a0e7319f2b5238f3ebc0a5cd419c92bf2c10045e1a8feae4222fce89b8b6287',
            'parentHash': '0x0eb7f809b8cbbd7cf73a56654f2614e3136a0d3496cacaf709dab2da515e568f',
            'number': 10647520,
            'timestamp': 1675576398,
            'nonce': '0x0000000000000000',
            'difficulty': 0,
            'gasLimit': {
                'type': 'BigNumber',
                'hex': '0x02625a00'
            },
            'gasUsed': {
                'type': 'BigNumber',
                'hex': '0x00'
            },
            'miner': '0xd98b305a9d433f062d44c1D542cdc25ECC0F0a40',
            'extraData': '0x',
            'transactions': [],
            'baseFeePerGas': {
                'type': 'BigNumber',
                'hex': '0x04a817c800'
            },
            '_difficulty': {
                'type': 'BigNumber',
                'hex': '0x00'
            }
        }
    }
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_parse_response_error_on_finalized_bundle_fetching(patch_base_class, monkeypatch):
    stream = KyveStream(config, pool_data)

    input_request = requests.Response()
    inputs = {"response": input_request, "stream_state": {}}

    mock_finalized_bundles_request = MagicMock(side_effect=IndexError)
    monkeypatch.setattr('requests.Response.json', mock_finalized_bundles_request)

    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = KyveStream(config, pool_data)
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request headers
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = KyveStream(config, pool_data)
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
    stream = KyveStream(config, pool_data)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = KyveStream(config, pool_data)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
