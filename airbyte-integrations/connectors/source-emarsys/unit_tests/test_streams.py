#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import re
from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import MagicMock

import pytz
import pytest
from airbyte_cdk.models.airbyte_protocol import SyncMode
from source_emarsys.streams import ContactLists, Contacts, EmarsysStream, PaginatedEmarsysStream, EmarsysAuthenticator


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(EmarsysStream, "path", "v0/example_endpoint")
    mocker.patch.object(EmarsysStream, "primary_key", "test_primary_key")
    mocker.patch.object(EmarsysStream, "__abstractmethods__", set())


@pytest.fixture
def patch_paginated_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PaginatedEmarsysStream, "path", "v0/example_endpoint")
    mocker.patch.object(PaginatedEmarsysStream, "primary_key", "test_primary_key")
    mocker.patch.object(PaginatedEmarsysStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = EmarsysStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_request_params__paginated_stream(patch_paginated_class):
    stream = PaginatedEmarsysStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"offset": 0, "limit": 10000}
    assert stream.request_params(**inputs) == expected_params


def test_request_params__paginated_stream__next_page_token(patch_paginated_class):
    stream = PaginatedEmarsysStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 10000}}
    expected_params = {"offset": 10000, "limit": 10000}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token__data_empty__return_none(patch_paginated_class):
    stream = PaginatedEmarsysStream()
    mock = MagicMock()
    mock.json.return_value = {"data": []}
    inputs = {"response": mock}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token__data_exists__return_offset(patch_paginated_class):
    stream = PaginatedEmarsysStream()
    mock = MagicMock()
    mock.json.return_value = {"data": [1, 2, 3]}
    mock.request.url = "http://api.com?offset=7"
    inputs = {"response": mock}
    expected_token = {"offset": 10}
    assert stream.next_page_token(**inputs) == expected_token


@pytest.mark.parametrize("payload, expected", (({}, None), ({"data": [1, 2, 3]}, 1), ({"not_data": "abc"}, None)))
def test_parse_response__return_data(payload, expected, patch_base_class):
    stream = EmarsysStream()
    mock = MagicMock()
    mock.json.return_value = payload
    inputs = {"response": mock}
    assert next(stream.parse_response(**inputs), None) == expected


def test_authenticator__get_auth_header():
    auth = EmarsysAuthenticator("user1", "password")
    pattern = r'UsernameToken Username="user1", PasswordDigest="[a-zA-Z0-9+=/]+", Nonce="[a-zA-Z0-9]+", Created="\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00"'
    request = MagicMock()
    request.headers = {}
    auth_request = auth(request)
    assert "X-WSSE" in auth_request.headers
    assert re.match(pattern, auth_request.headers["X-WSSE"])


def test_request_headers(patch_base_class):
    stream = EmarsysStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = EmarsysStream()
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
    stream = EmarsysStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time__no_rate_limit__one_sec(patch_base_class):
    response_mock = MagicMock()
    stream = EmarsysStream()
    expected_backoff_time = 1
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_backoff_time__rate_limit(patch_base_class):
    response_mock = MagicMock()
    reset_dt = datetime.utcnow() + timedelta(seconds=60)
    response_mock.headers = {"X-Ratelimit-Reset": str(int(reset_dt.replace(tzinfo=pytz.UTC).timestamp()))}
    stream = EmarsysStream()
    expected_backoff_time = 59
    assert stream.backoff_time(response_mock) > expected_backoff_time


def test_backoff_time__stale_rate_limit__one_sec(patch_base_class):
    response_mock = MagicMock()
    reset_dt = datetime.utcnow() - timedelta(seconds=60)
    response_mock.headers = {"X-Ratelimit-Reset": str(int(reset_dt.replace(tzinfo=pytz.UTC).timestamp()))}
    stream = EmarsysStream()
    expected_backoff_time = 1
    assert stream.backoff_time(response_mock) == expected_backoff_time


@pytest.fixture
def mock_get_fields(mocker):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"id": 1, "string_id": "field_a", "application_type": "bigtext"},
            {"id": 2, "string_id": "field_b", "application_type": "numeric"},
            {"id": 3, "string_id": "field_c", "application_type": "date"},
        ]
    }
    mocker.patch("source_emarsys.streams.requests.Session.get", return_value=mock_response)


def test_contacts_build_field_mapping(mock_get_fields):
    stream = Contacts(parent=ContactLists(), fields=["field_x"])
    field_dict, field_string_2_id = stream._build_field_mapping()
    expected_field_dict = {
        "1": {"id": 1, "string_id": "field_a", "application_type": "bigtext"},
        "2": {"id": 2, "string_id": "field_b", "application_type": "numeric"},
        "3": {"id": 3, "string_id": "field_c", "application_type": "date"},
    }
    expected_field_string_2_id = {"field_a": "1", "field_b": "2", "field_c": "3"}
    assert expected_field_dict == field_dict
    assert expected_field_string_2_id == field_string_2_id


@pytest.mark.parametrize(
    "contact_lists, expected_contact_lists",
    (
        (
            [
                {"id": 1, "name": "list a", "created": "0001-01-01 00:00:00"},
                {"id": 2, "name": "recur old", "created": "0002-02-02 00:00:00"},
                {"id": 3, "name": "list b", "created": "0003-03-03 00:00:00"},
                {"id": 4, "name": "recur new", "created": "0004-04-04 00:00:00"},
            ],
            [
                {"parent": {"id": 1, "name": "list a", "created": "0001-01-01 00:00:00"}},
                {"parent": {"id": 3, "name": "list b", "created": "0003-03-03 00:00:00"}},
                {"parent": {"id": 4, "name": "recur new", "created": "0004-04-04 00:00:00"}},
            ],
        ),
        (
            [
                {"id": 1, "name": "list a", "created": "0001-01-01 00:00:00"},
                {"id": 2, "name": "list b", "created": "0003-03-03 00:00:00"},
            ],
            [
                {"parent": {"id": 1, "name": "list a", "created": "0001-01-01 00:00:00"}},
                {"parent": {"id": 2, "name": "list b", "created": "0003-03-03 00:00:00"}},
            ],
        ),
        (
            [
                {"id": 1, "name": "recur old", "created": "0002-02-02 00:00:00"},
                {"id": 2, "name": "recur new", "created": "0004-04-04 00:00:00"},
                {"id": 3, "name": "recur very new", "created": "2022-03-03 00:00:00"},
            ],
            [
                {"parent": {"id": 3, "name": "recur very new", "created": "2022-03-03 00:00:00"}},
            ],
        ),
    ),
)
def test_contacts__stream_slices(contact_lists, expected_contact_lists, mocker):
    mocker.patch("source_emarsys.streams.ContactLists.read_records", return_value=iter(contact_lists))
    stream = Contacts(parent=ContactLists(), fields=["field_x"], recur_list_patterns=["^recur.*"])
    inputs = {"sync_mode": SyncMode.full_refresh, "cursor_field": None, "stream_state": None}
    assert list(stream.stream_slices(**inputs)) == expected_contact_lists


def test_contacts__request_params(mock_get_fields):
    stream = Contacts(parent=ContactLists(), fields=["field_a", "field_b", "field_c"])
    expected_param_fields = "1,2,3"
    inputs = {"stream_state": None, "stream_slice": None, "next_page_token": None}
    assert stream.request_params(**inputs)["fields"] == expected_param_fields


def test_contacts__get_airbyte_format(mock_get_fields):
    stream = Contacts(parent=ContactLists(), fields=[])
    assert stream.get_airbyte_format("field_a") == {"type": ["null", "string"]}
    assert stream.get_airbyte_format("field_b") == {"type": ["null", "number"]}
    assert stream.get_airbyte_format("field_c") == {"type": ["null", "string"], "format": "date"}


def test_contacts__get_json_schema(mock_get_fields):
    stream = Contacts(parent=ContactLists(), fields=["field_a", "field_b", "field_c"])
    expected_schema_properties = {
        "id": {"type": ["null", "string"]},
        "uid": {"type": ["null", "string"]},
        "field_a": {"type": ["null", "string"]},
        "field_b": {"type": ["null", "number"]},
        "field_c": {"type": ["null", "string"], "format": "date"},
    }
    assert stream.get_json_schema()["properties"] == expected_schema_properties


def test_contacts__parse_response(mock_get_fields):
    stream = Contacts(parent=ContactLists(), fields=[])
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "1": {"fields": {"id": "1", "uid": "1a", "1": "aaa", "2": 111, "3": "0001-01-01 00:00:00"}},
            "2": {"fields": {"id": "2", "uid": "2a", "1": None, "2": None, "3": None}},
        }
    }
    inputs = {"response": mock_response, "stream_state": None, "stream_slice": None, "next_page_token": None}
    expected = [
        {"id": "1", "uid": "1a", "field_a": "aaa", "field_b": 111, "field_c": "0001-01-01 00:00:00"},
        {"id": "2", "uid": "2a", "field_a": None, "field_b": None, "field_c": None},
    ]
    assert list(stream.parse_response(**inputs)) == expected
