#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
import json
from unittest.mock import MagicMock

import pytest
import requests
import responses
from source_pendo_python.source import SourcePendoPython
from source_pendo_python.streams import (
  PendoPythonStream,
  PendoAggregationStream,
  Feature,
  Guide,
  Page,
  Report,
  VisitorMetadata,
  AccountMetadata,
  Visitors,
  Accounts
)

fake_token = 'ABC123'
page_size = 10
aggregation_primary_key = 'test_id'


@pytest.fixture(name="config")
def config_fixture():
    return {"api_key": fake_token}


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PendoPythonStream, "url_base", "https://app.pendo.io/api/v1/")
    mocker.patch.object(PendoPythonStream, "primary_key", "id")
    mocker.patch.object(PendoPythonStream, "__abstractmethods__", set())


def test_base_http_method(patch_base_class):
    stream = PendoPythonStream()
    expected_method = "GET"
    assert stream.http_method == expected_method


def test_base_next_page_token(patch_base_class):
    stream = PendoPythonStream()
    assert stream.next_page_token({}) is None


def test_request_params(patch_base_class):
    stream = PendoPythonStream()
    expected_params = {}
    assert stream.request_params({}) == expected_params


def test_parse_response(patch_base_class):
    stream = PendoPythonStream()
    response = MagicMock()
    expected_parsed_object = [
        {"test_id": "id1"},
        {"test_id": "id2"}
    ]
    response.json.return_value = expected_parsed_object
    inputs = {"response": response}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object[0]


def test_get_valid_field_info(patch_base_class):
    stream = PendoPythonStream()
    input = "time"
    assert stream.get_valid_field_info(input) == {
        "type": ["null", "integer"]
    }
    input = "list"
    assert stream.get_valid_field_info(input) == {
        "type": ["null", "array"]
    }
    input = ""
    assert stream.get_valid_field_info(input) == {
        "type": ["null", "array", "string", "integer", "boolean"]
    }
    input = "random"
    assert stream.get_valid_field_info(input) == {
        "type": ["null", "random"]
    }


# THE FOLLOWING TEST THE PendoAggregationStream SUBCLASS
@pytest.fixture
def patch_aggregation_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PendoAggregationStream, "url_base", "https://app.pendo.io/api/v1/")
    mocker.patch.object(PendoAggregationStream, "primary_key", aggregation_primary_key)
    mocker.patch.object(PendoAggregationStream, "json_schema", None)
    mocker.patch.object(PendoAggregationStream, "page_size", page_size)
    mocker.patch.object(PendoAggregationStream, "__abstractmethods__", set())


def test_http_method(patch_aggregation_class):
    stream = PendoAggregationStream()
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_path(patch_aggregation_class):
    stream = PendoAggregationStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    assert stream.path(**inputs) == "aggregation"


def test_request_headers(patch_aggregation_class):
    stream = PendoAggregationStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"Content-Type": "application/json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_next_page_token(patch_aggregation_class):
    stream = PendoAggregationStream()
    response = MagicMock()
    response.json.return_value = {"results": [
        {"test_id": "id1"},
        {"test_id": "id2"},
        {"test_id": "id3"},
        {"test_id": "id4"},
        {"test_id": "id5"},
        {"test_id": "id6"},
        {"test_id": "id7"},
        {"test_id": "id8"},
        {"test_id": "id9"},
        {"test_id": "id10"}
    ]}
    inputs = {"response": response}
    expected_token = "id10"
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_end(patch_aggregation_class):
    stream = PendoAggregationStream()
    response = MagicMock()
    response.json.return_value = {"results": [
        {"test_id": "id1"},
        {"test_id": "id2"}
    ]}
    inputs = {"response": response}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_build_request_body_initial(patch_aggregation_class):
    requestId = "test-list"
    source = {"tests": {}}
    stream = PendoAggregationStream()
    inputs = {"requestId": requestId, "source": source, "next_page_token": None}
    expected_body = {
        "response": {"mimeType": "application/json"},
        "request": {
            "requestId": requestId,
            "pipeline": [
                {"source": source},
                {"sort": [aggregation_primary_key]},
                {"limit": page_size},
            ],
        },
    }
    assert stream.build_request_body(**inputs) == expected_body


def test_build_request_body_pagination(patch_aggregation_class):
    requestId = "test-list"
    source = {"tests": {}}
    next_page_token = "lastid-from-prev-response"
    stream = PendoAggregationStream()
    inputs = {"requestId": requestId, "source": source, "next_page_token": next_page_token}
    expected_body = {
        "response": {"mimeType": "application/json"},
        "request": {
            "requestId": requestId,
            "pipeline": [
                {"source": source},
                {"sort": [aggregation_primary_key]},
                {"filter": f"{aggregation_primary_key} > \"{next_page_token}\""},
                {"limit": page_size},
            ],
        },
    }
    assert stream.build_request_body(**inputs) == expected_body


# @pytest.mark.parametrize(
#     ("http_status", "should_retry"),
#     [
#         (HTTPStatus.OK, False),
#         (HTTPStatus.BAD_REQUEST, False),
#         (HTTPStatus.TOO_MANY_REQUESTS, True),
#         (HTTPStatus.INTERNAL_SERVER_ERROR, True),
#     ],
# )
# def test_should_retry(patch_base_class, http_status, should_retry):
#     response_mock = MagicMock()
#     response_mock.status_code = http_status
#     stream = PendoPythonStream()
#     assert stream.should_retry(response_mock) == should_retry


# def test_backoff_time(patch_base_class):
#     response_mock = MagicMock()
#     stream = PendoPythonStream()
#     expected_backoff_time = None
#     assert stream.backoff_time(response_mock) == expected_backoff_time


# def test_account_stream(config):
#     authenticator = SourcePendoPython._get_authenticator(config)
#     stream = Accounts(authenticator)
#     assert True is True


# def test_feature_stream():
#     stream = Feature()
#     assert True is True


# def test_guide_stream():
#     stream = Guide()
#     assert True is True


# def test_page_stream():
#     stream = Page()
#     assert True is True


# def test_report_stream():
#     stream = Report()
#     assert True is True


# def test_account_metadata_stream():
#     stream = AccountMetadata()
#     assert True is True


# def test_visitor_metadata_stream():
#     stream = VisitorMetadata()
#     assert True is True


# def test_visitor_stream():
#     stream = Visitors()
#     assert True is True
