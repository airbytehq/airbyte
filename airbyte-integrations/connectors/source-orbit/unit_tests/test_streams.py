#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_orbit.streams import Members, OrbitStream, OrbitStreamPaginated


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(OrbitStream, "path", "v0/example_endpoint")
    mocker.patch.object(OrbitStream, "primary_key", "test_primary_key")
    mocker.patch.object(OrbitStream, "__abstractmethods__", set())
    mocker.patch.object(OrbitStreamPaginated, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = OrbitStream(workspace="workspace")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = OrbitStream(workspace="workspace")
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, mocker):
    stream = OrbitStream(workspace="workspace")
    inputs = {"response": mocker.Mock(json=mocker.Mock(return_value={"data": ["foo", "bar"]}))}
    gen = stream.parse_response(**inputs)
    assert next(gen) == "foo"
    assert next(gen) == "bar"


def test_request_headers(patch_base_class):
    stream = OrbitStream(workspace="workspace")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = OrbitStream(workspace="workspace")
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
    stream = OrbitStream(workspace="workspace")
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = OrbitStream(workspace="workspace")
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


class TestOrbitStreamPaginated:
    @pytest.mark.parametrize(
        "json_response, expected_token", [({"links": {"next": "http://foo.bar/api?a=b&c=d"}}, {"a": "b", "c": "d"}), ({}, None)]
    )
    def test_next_page_token(self, patch_base_class, mocker, json_response, expected_token):
        stream = OrbitStreamPaginated(workspace="workspace")
        inputs = {"response": mocker.Mock(json=mocker.Mock(return_value=json_response))}
        assert stream.next_page_token(**inputs) == expected_token


class TestMembers:
    @pytest.mark.parametrize("start_date", [None, "2022-06-27"])
    def test_members_request_params(self, patch_base_class, start_date):
        stream = Members(workspace="workspace", start_date=start_date)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        if start_date is not None:
            expected_params = {"sort": "created_at", "start_date": start_date}
        else:
            expected_params = {"sort": "created_at"}
        assert stream.request_params(**inputs) == expected_params
