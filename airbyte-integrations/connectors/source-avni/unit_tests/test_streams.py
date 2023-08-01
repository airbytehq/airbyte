#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_avni.source import AvniStream


@pytest.fixture
def patch_base_class(mocker):

    mocker.patch.object(AvniStream, "path", "v0/example_endpoint")
    mocker.patch.object(AvniStream, "primary_key", "test_primary_key")
    mocker.patch.object(AvniStream, "__abstractmethods__", set())


def test_request_params(mocker,patch_base_class):

    stream = AvniStream(start_date="",auth_token="",path="")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page":5}}
    stream.state = {"Last modified at":"AnyDate"}
    expected_params = {"lastModifiedDateTime":"AnyDate","page":5}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):

    stream = AvniStream(start_date="",auth_token="",path="")
    response_mock = MagicMock()
    response_mock.json.return_value = {
        "totalElements": 20,
        "totalPages": 10,
        "pageSize": 20
    }

    stream.current_page = 1
    inputs = {"response": response_mock}
    expected_token = {"page": 2}

    assert stream.next_page_token(**inputs) == expected_token
    assert stream.current_page == 2


def test_parse_response(patch_base_class,mocker):

    stream = AvniStream(start_date="",auth_token="",path="")
    response = MagicMock
    response.content = b'{"content": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]}'

    inputs = {"response": mocker.Mock(json=mocker.Mock(return_value={"content": [{"id": 1, "name": "Avni"}, {"id": 2, "name": "Airbyte"}]}))}
    gen = stream.parse_response(**inputs)
    assert next(gen) == {"id": 1, "name": "Avni"}
    assert next(gen) == {"id": 2, "name": "Airbyte"}


def test_request_headers(patch_base_class):

    stream = AvniStream(start_date="",auth_token="",path="")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    stream.auth_token = "Token"
    expected_headers = {"auth-token":"Token"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):

    stream = AvniStream(start_date="",auth_token="",path="")
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
    stream = AvniStream(start_date="",auth_token="",path="")
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):

    response_mock = MagicMock()
    stream = AvniStream(start_date="",auth_token="",path="")
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
