#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import responses
from source_maestro_qa.source import MaestroQAExportStream, MaestroQAStream

from .helpers import data_url, setup_bad_response, setup_good_response


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(MaestroQAStream, "path", "request-groups-export")
    mocker.patch.object(MaestroQAStream, "primary_key", "test_primary_key")
    mocker.patch.object(MaestroQAStream, "__abstractmethods__", set())
    mocker.patch.object(MaestroQAExportStream, "path", "request-groups-export")
    mocker.patch.object(MaestroQAExportStream, "primary_key", "test_primary_key")
    mocker.patch.object(MaestroQAExportStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = MaestroQAStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = MaestroQAStream()
    inputs = {"response": MagicMock(json=MagicMock(return_value={"data": []}))}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = MaestroQAStream()
    inputs = {"response": MagicMock(json=MagicMock(return_value={"data": [{"key": "value"}]}))}
    expected_parsed_object = [{"key": "value"}]
    assert stream.parse_response(**inputs) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = MaestroQAStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = MaestroQAStream()
    expected_method = "POST"
    assert stream.http_method == expected_method


@responses.activate
def test_download_data(patch_base_class):
    setup_good_response()

    stream = MaestroQAExportStream()
    inputs = {"url": data_url}
    expected_data = {
        "group_name": "All Agents",
        "group_id": "groupid1",
        "agent_name": "Jon Doe",
        "agent_email": "john@doe.com",
        "agent_ids": "10061553646875",
        "available": "False",
    }
    assert next(stream.download_data(**inputs)) == expected_data


@responses.activate
def test_create_export_job(patch_base_class):
    setup_good_response()

    stream = MaestroQAExportStream()
    inputs = {"path": stream.path, "headers": {}, "json": {}}
    expected_job = "123"
    assert stream.create_export_job(**inputs) == expected_job


@responses.activate
def test_create_export_job_error(patch_base_class):
    setup_bad_response()

    stream = MaestroQAExportStream()
    inputs = {"path": stream.path, "headers": {}, "json": {}}
    with pytest.raises(Exception):
        stream.create_export_job(**inputs)


@responses.activate
def test_wait_for_job(patch_base_class):
    setup_good_response()

    stream = MaestroQAExportStream()
    inputs = {"export_id": "123", "headers": {}}
    assert stream.wait_for_job(**inputs) == data_url


@responses.activate
def test_wait_for_job_error(patch_base_class):
    setup_bad_response()

    stream = MaestroQAExportStream()
    inputs = {"export_id": "123", "headers": {}}
    with pytest.raises(Exception):
        stream.wait_for_job(**inputs)


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
    stream = MaestroQAStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = MaestroQAStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
