#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from requests.models import Response
from source_opentable_sync_api.source import OpentableSyncAPIStream

start_date = "2021-10-01T10:00:00Z"


the_response = Response()
the_response.code = "expired"
the_response.error_type = "expired"
the_response.status_code = 400
the_response._content = b'{"hasNextPage":"true", "nextPageUrl":"url", "items":[{"id":1}]}'


@pytest.fixture
def patch_base_class(mocker, config):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(OpentableSyncAPIStream, "path", "v0/example_endpoint")
    mocker.patch.object(OpentableSyncAPIStream, "primary_key", "test_primary_key")
    mocker.patch.object(OpentableSyncAPIStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    # TODO: replace this with your input parameters
    dt_start_date = datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%SZ")
    inputs = {"stream_slice": {"start_date": dt_start_date, "rid": "134250"}, "stream_state": None, "next_page_token": None}
    print(stream.request_params(**inputs))
    # TODO: replace this with your expected request parameters
    expected_params = {"limit": 1000, "offset": 0, "rid": "134250", "updated_after": "2021-10-01T10:00:00Z"}
    assert stream.request_params(**inputs) == expected_params


def test_request_headers(patch_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request headers
    expected_headers = {"Content-Type": "application/json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_next_page_token(patch_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    # TODO: replace this with your input parameters
    inputs = {"response": the_response}
    # TODO: replace this with your expected next page token
    expected_token = {"nextPageUrl": "url"}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    # TODO: replace this with your input parameters
    inputs = {"response": the_response}
    # TODO: replace this with your expected parced object
    expected_parsed_object = {"id": 1}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_http_method(patch_base_class, config):
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
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
def test_should_retry(patch_base_class, http_status, should_retry, config):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class, config):
    response_mock = MagicMock()
    stream = OpentableSyncAPIStream(config, start_date=config["start_date"], rid_list=config["rid_list"])
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
