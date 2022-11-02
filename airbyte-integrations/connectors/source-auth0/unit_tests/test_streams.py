#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from abc import ABC
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.models import SyncMode
from source_auth0.source import Auth0Stream, IncrementalAuth0Stream, Users


@pytest.fixture
def patch_base_class(mocker):
    """
    Base patcher for used streams
    """
    mocker.patch.object(Auth0Stream, "primary_key", "test_primary_key")
    mocker.patch.object(Auth0Stream, "__abstractmethods__", set())
    mocker.patch.object(IncrementalAuth0Stream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalAuth0Stream, "__abstractmethods__", set())


class TestAuth0Stream:
    def test_auth0_stream_request_params(self, patch_base_class, url_base):
        stream = Auth0Stream(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {
            "page": 0,
            "per_page": 50,
            "include_totals": "true",
        }
        assert stream.request_params(**inputs) == expected_params

    def test_auth0_stream_parse_response(self, patch_base_class, requests_mock, url_base, api_url):
        stream = Auth0Stream(url_base=url_base)
        requests_mock.get(f"{api_url}", json={"entities": [{"a": 123}, {"b": "xx"}]})
        resp = requests.get(f"{api_url}")
        inputs = {"response": resp, "stream_state": MagicMock()}
        expected_parsed_object = [{"a": 123}, {"b": "xx"}]
        assert list(stream.parse_response(**inputs)) == expected_parsed_object

    def test_auth0_stream_backoff_time(self, patch_base_class, url_base):
        response_mock = requests.Response()
        stream = Auth0Stream(url_base=url_base)
        expected_backoff_time = None
        assert stream.backoff_time(response_mock) == expected_backoff_time

    def test_auth0_stream_incremental_request_params(self, patch_base_class, url_base):
        stream = IncrementalAuth0Stream(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {
            "page": 0,
            "per_page": 50,
            "include_totals": "false",
            "sort": "None:1",
            "q": "None:{ TO *]",
        }
        assert stream.request_params(**inputs) == expected_params

    def test_incremental_auth0_stream_parse_response(self, patch_base_class, requests_mock, url_base, api_url):
        stream = IncrementalAuth0Stream(url_base=url_base)
        requests_mock.get(f"{api_url}", json=[{"a": 123}, {"b": "xx"}])
        resp = requests.get(f"{api_url}")
        inputs = {"response": resp, "stream_state": MagicMock()}
        expected_parsed_object = [{"a": 123}, {"b": "xx"}]
        assert list(stream.parse_response(**inputs)) == expected_parsed_object

    def test_incremental_auth0_stream_backoff_time(self, patch_base_class, url_base):
        response_mock = MagicMock()
        stream = IncrementalAuth0Stream(url_base=url_base)
        expected_backoff_time = None
        assert stream.backoff_time(response_mock) == expected_backoff_time

    def test_auth0_stream_incremental_backoff_time_empty(self, patch_base_class, url_base):
        stream = IncrementalAuth0Stream(url_base=url_base)
        response = MagicMock(requests.Response)
        response.status_code = 200
        expected_params = None
        inputs = {"response": response}
        assert stream.backoff_time(**inputs) == expected_params

    def test_auth0_stream_incremental_back_off_now(self, patch_base_class, url_base):
        stream = IncrementalAuth0Stream(url_base=url_base)
        response = MagicMock(requests.Response)
        response.status_code = requests.codes.TOO_MANY_REQUESTS
        response.headers = {"x-ratelimit-reset": int(time.time())}
        expected_params = (0, 2)
        inputs = {"response": response}
        get_backoff_time = stream.backoff_time(**inputs)
        assert expected_params[0] <= get_backoff_time <= expected_params[1]

    def test_auth0_stream_incremental_get_updated_state(self, patch_base_class, latest_record_instance, url_base):
        class TestIncrementalAuth0Stream(IncrementalAuth0Stream, ABC):
            cursor_field = "lastUpdated"

        stream = TestIncrementalAuth0Stream(url_base=url_base)
        stream._cursor_field = "lastUpdated"
        assert stream._cursor_value == ""
        stream.state = {"lastUpdated": "123"}
        assert stream._cursor_value == "123"

    def test_auth0_stream_http_method(self, patch_base_class, url_base):
        stream = Auth0Stream(url_base=url_base)
        expected_method = "GET"
        assert stream.http_method == expected_method


class TestNextPageToken:
    def test_next_page_token(self, patch_base_class, url_base):
        stream = Auth0Stream(url_base=url_base)
        json = {
            "start": "0",
            "limit": 50,
            "length": "50",
            "total": 51,
        }
        response = MagicMock(requests.Response)
        response.json = MagicMock(return_value=json)
        inputs = {"response": response}
        expected_token = {"page": 1, "per_page": 50}
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_invalid_cursor(self, patch_base_class, url_base):
        stream = Auth0Stream(url_base=url_base)
        json = {
            "start": "0",
            "limit": 50,
            "length": "abc",
            "total": 51,
        }
        response = MagicMock(requests.Response)
        response.json = MagicMock(return_value=json)
        inputs = {"response": response}
        expected_token = None
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_missing_cursor(self, patch_base_class, url_base):
        stream = Auth0Stream(url_base=url_base)
        json = {
            "limit": 50,
            "total": 51,
        }
        response = MagicMock(requests.Response)
        response.json = MagicMock(return_value=json)
        inputs = {"response": response}
        expected_token = None
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_one_page_only(self, patch_base_class, url_base):
        stream = Auth0Stream(url_base=url_base)
        json = {
            "start": 0,
            "limit": 50,
            "length": 1,
            "total": 1,
        }
        response = MagicMock(requests.Response)
        response.json = MagicMock(return_value=json)
        inputs = {"response": response}
        expected_token = None
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_last_page_incomplete(self, patch_base_class, url_base):
        stream = Auth0Stream(url_base=url_base)
        json = {
            "start": "50",
            "limit": 50,
            "length": "1",
            "total": 51,
        }
        response = MagicMock(requests.Response)
        response.json = MagicMock(return_value=json)
        inputs = {"response": response}
        expected_token = None
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_last_page_complete(self, patch_base_class, url_base):
        stream = Auth0Stream(url_base=url_base)
        json = {
            "start": "50",
            "limit": 50,
            "length": "50",
            "total": 100,
        }
        response = MagicMock(requests.Response)
        response.json = MagicMock(return_value=json)
        inputs = {"response": response}
        expected_token = None
        result = stream.next_page_token(**inputs)
        assert result == expected_token


class TestStreamUsers:
    def test_stream_users(self, patch_base_class, users_instance, url_base, api_url, requests_mock):
        stream = Users(url_base=url_base)
        requests_mock.get(
            f"{api_url}/users",
            json=[users_instance],
        )
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == [users_instance]

    def test_users_request_params_out_of_next_page_token(self, patch_base_class, url_base):
        stream = Users(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {
            "include_totals": "false",
            "page": 0,
            "per_page": 50,
            "q": "updated_at:{1900-01-01T00:00:00.000Z TO *]",
            "sort": "updated_at:1",
        }
        assert stream.request_params(**inputs) == expected_params

    def test_users_source_request_params_have_next_cursor(self, patch_base_class, url_base):
        stream = Users(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page": 1, "per_page": 50}}
        expected_params = {
            "include_totals": "false",
            "page": 1,
            "per_page": 50,
            "q": "updated_at:{1900-01-01T00:00:00.000Z TO *]",
            "sort": "updated_at:1",
        }
        assert stream.request_params(**inputs) == expected_params

    def test_users_source_parse_response(self, requests_mock, patch_base_class, users_instance, url_base, api_url):
        stream = Users(url_base=url_base)
        requests_mock.get(
            f"{api_url}/users",
            json=[users_instance],
        )
        assert list(stream.parse_response(response=requests.get(f"{api_url}/users"))) == [users_instance]
