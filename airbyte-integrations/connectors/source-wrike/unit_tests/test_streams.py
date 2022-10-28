#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pendulum
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from pytest import fixture, mark
from source_wrike.source import Comments, Tasks, WrikeStream, to_utc_z


@fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(WrikeStream, "__abstractmethods__", set())


@fixture()
def args(request):
    args = {"wrike_instance": "app-us2.wrike.com", "authenticator": TokenAuthenticator(token="tokkk")}
    return args


def test_request_params(args):
    stream = WrikeStream(**args)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = None
    assert stream.request_params(**inputs) == expected_params


def test_tasks_request_params(args):
    stream = Tasks(**args)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    assert stream.request_params(**inputs).get("fields")


def test_comments_slices(args):
    stream = Comments(start_date=pendulum.parse("2022-05-01"), **args)
    inputs = {"stream_state": None}
    slices = list(stream.stream_slices(**inputs))
    assert slices[0].get("start") == "2022-05-01T00:00:00Z"
    assert len(slices) > 1


def test_next_page_token(args):
    stream = WrikeStream(**args)

    response = MagicMock()
    # first page
    response.json.return_value = {
        "kind": "tasks",
        "nextPageToken": "ADE7SXYAAAAAUAAAAAAQAAAAMAAAAAABVB5K4QPE7SXKM",
        "responseSize": 96,
        "data": [{"id": "IEAFHZ6ZKQ233LQK"}],
    }
    inputs = {"response": response}
    expected_token = {"nextPageToken": "ADE7SXYAAAAAUAAAAAAQAAAAMAAAAAABVB5K4QPE7SXKM"}
    assert stream.next_page_token(**inputs) == expected_token
    # next page
    response.json.return_value = {
        "kind": "tasks",
        "responseSize": 96,
        "data": [{"id": "IEAFHZ6ZKQ233LQK"}],
    }
    inputs = {"response": response}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(args):
    stream = WrikeStream(**args)
    response = MagicMock()
    response.json.return_value = {
        "kind": "tasks",
        "responseSize": 96,
        "data": [{"id": "IEAFHZ6ZKQ233LQK"}],
    }
    inputs = {"response": response}
    expected_parsed_object = {"id": "IEAFHZ6ZKQ233LQK"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(args):
    stream = WrikeStream(**args)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(args):
    stream = WrikeStream(**args)
    expected_method = "GET"
    assert stream.http_method == expected_method


@mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(args, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = WrikeStream(**args)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(args):
    response_mock = MagicMock()
    stream = WrikeStream(**args)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_to_utc_z():
    assert to_utc_z(pendulum.parse("2022-05-01")) == "2022-05-01T00:00:00Z"
