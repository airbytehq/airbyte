#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_gainsight_cs.streams import GainsightCsStream, GainsightCsObjectStream

GAINSIGHT_DOMAIN_URL = "https://fake-domain.gainsightcloud.com"
GAINSIGHT_STREAM_NAME = "fake_name"


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(GainsightCsStream, "url_base", f"{GAINSIGHT_DOMAIN_URL}/v1/")
    mocker.patch.object(GainsightCsStream, "__abstractmethods__", set())
    mocker.patch.object(GainsightCsObjectStream, "limit", 5)
    mocker.patch.object(GainsightCsObjectStream, "offset", 0)


def test_request_params(patch_base_class):
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    response = MagicMock()
    records = [{"test_id": "id1"}, {"test_id": "id2"}, {"test_id": "id3"}, {"test_id": "id4"}, {"test_id": "id5"}]
    response.json.return_value = {
        "data": {
            "records": records
        }
    }
    inputs = {"response": response}
    expected_token = stream.offset + stream.limit
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_end(patch_base_class):
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    response = MagicMock()
    records = [{"test_id": "id1"}, {"test_id": "id2"}]
    response.json.return_value = {
        "data": {
            "records": records
        }
    }
    inputs = {"response": response}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    response = MagicMock()
    records = [{"test_id": "id1"}, {"test_id": "id2"}]
    expected_parsed_object = {
        "data": {
            "records": records
        }
    }
    response.json.return_value = expected_parsed_object
    inputs = {"response": response}
    assert next(stream.parse_response(**inputs)) == records[0]


def test_request_headers(patch_base_class):
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_path(patch_base_class):
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    assert stream.path(**inputs) == f"data/objects/query/{GAINSIGHT_STREAM_NAME}"


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
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = GainsightCsObjectStream(name=GAINSIGHT_STREAM_NAME, domain_url=GAINSIGHT_DOMAIN_URL)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
