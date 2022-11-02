#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from requests import Response
from source_commcare.source import CommcareStream
from source_commcare.source import (
    Application,
    Form,
    FormCase
)


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(CommcareStream, "path", "v0/example_endpoint")
    # mocker.patch.object(CommcareStream, "primary_key", "test_primary_key")
    mocker.patch.object(CommcareStream, "__abstractmethods__", set())


@pytest.fixture(name="config")
def config_fixture():
    config = {"authenticator": "authenticator", 'api_key': 'apikey', 'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}
    return config


@pytest.mark.parametrize(
    "stream, expected, config",
    [
        (Application, "application/appid/", {'app_id': 'appid'}),
        (Form, "form", {'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}),
        (FormCase, "case",{'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}),
    ],
)
def test_path(
    stream,
    expected,
    config,
):
    assert stream(**config).path() == expected



@pytest.mark.parametrize(
    "stream, expected, config",
    [
        (Application, {'format': 'json', 'extras' : 'true'},{'app_id': 'appid'}),
        (Form, {"format": 'json', "offset": 0, "limit": 20, 'indexed_on_start': '2022-01-01T00:00:00.000000', 'order_by': 'indexed_on', 'app_id': 'appid'}, {'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}),
        (FormCase, {"format": 'json', "offset": 0, "limit": 20, 'indexed_on_start': '2022-01-01T00:00:00.000000', 'order_by': 'indexed_on'}, {'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}),
    ],
)
def test_request_params(patch_base_class, stream, expected, config):
    assert stream(**config).request_params(stream_state=None,stream_slice=None,next_page_token={"offset": 0, "limit": 20}) == expected

@pytest.mark.parametrize(
    "stream, expected, config",
    [
        (Application, None, {'app_id': 'appid'}),
        (Form, {'limit': ['20'], 'offset': ['0']}, {'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}),
        (FormCase, {'limit': ['20'], 'offset': ['0']},{'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}),
    ],
)
def test_next_page_token(patch_base_class, stream, expected, config):
    st = stream(**config)
    attr = {'json.return_value': {'meta': {'limit': 20, 'offset': 33, "next": '?limit=20&offset=0'}}}
    r = MagicMock(spec=Response)
    r.configure_mock(**attr)
    inputs = {'response': r}
    assert st.next_page_token(**inputs) == expected


@pytest.mark.parametrize(
    "strm, config",
    [
        # (Application, {'app_id': 'appid'}),
        (Form, {'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}),
        (FormCase, {'app_id': 'appid', 'start_date': '2022-01-01T00:00:00Z'}),
    ],
)
def test_parse_response(patch_base_class, strm, config):
    stream = strm(**config)
    objects = [{'test': 'test'}, {'test1': 'test1'}]
    attr = {'json.return_value': {'objects': objects}}
    r = MagicMock(spec=Response)
    r.configure_mock(**attr)
    inputs = {'response': r}
    expected_parsed_object = objects
    iter = stream.parse_response(**inputs)
    assert next(iter) == objects[0]
    expected_parsed_object = objects[1]
    assert next(iter) == expected_parsed_object

def test_parse_response_application(patch_base_class):
    stream = Application(**{'app_id': 'appid'})
    objects = [{'test': 'test'}, {'test1': 'test1'}]
    attr = {'json.return_value': {'objects': objects}}
    r = MagicMock(spec=Response)
    r.configure_mock(**attr)
    inputs = {'response': r}
    expected_parsed_object = {'objects': objects}
    iter = stream.parse_response(**inputs)
    assert next(iter) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = CommcareStream()
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request headers
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = CommcareStream()
    # TODO: replace this with your expected http request method
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
    stream = CommcareStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = CommcareStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
