#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import time
from http import HTTPStatus
from typing import Any, Mapping, Optional
from unittest.mock import MagicMock

import pytest
import requests
from source_okta.components import CustomBearerAuthenticator, CustomOauth2Authenticator
from source_okta.source import SourceOkta

from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> DefaultStream:
    source = SourceOkta(config=config)
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def get_retriever(stream: DefaultStream) -> SimpleRetriever:
    return stream._stream_partition_generator._partition_factory._retriever


def get_backoff_time(stream: DefaultStream, response: requests.Response) -> Optional[float]:
    for backoff_strategy in get_retriever(stream).requester.error_handler.backoff_strategies:
        backoff_time = backoff_strategy.backoff_time(response_or_exception=response, attempt_count=0)
        if backoff_time:
            return backoff_time
    return None


def get_next_page_token(stream: DefaultStream, response: requests.Response) -> Optional[Mapping[str, Any]]:
    return get_retriever(stream)._next_page_token(response=response, last_page_size=0, last_record=None, last_page_token_value=None)


class TestStatusCodes:
    @pytest.mark.parametrize(
        ("http_status", "should_retry"),
        [
            (HTTPStatus.OK, False),
            (HTTPStatus.BAD_REQUEST, False),
            (HTTPStatus.TOO_MANY_REQUESTS, True),
            (HTTPStatus.INTERNAL_SERVER_ERROR, True),
        ],
    )
    def test_should_retry(self, http_status, should_retry, url_base, start_date, requests_mock, oauth_config, api_url):
        oauth_kwargs = {key: value for key, value in oauth_config.get("credentials").items() if key != "auth_type"}
        oauth_kwargs["token_refresh_endpoint"] = f"{api_url}/oauth2/v1/token"
        oauth_authentication_instance = CustomOauth2Authenticator(config=oauth_config, **oauth_kwargs, parameters=None)
        oauth_authentication_instance.path = f"{api_url}/oauth2/v1/token"
        assert isinstance(oauth_authentication_instance, CustomOauth2Authenticator)
        source_okta = SourceOkta(config=oauth_config)
        requests_mock.get(f"{api_url}/api/v1/users?limit=1", status_code=400, json={})
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"access_token": "test_token", "expires_in": 948})
        response_mock = requests.Response()
        response_mock.status_code = http_status
        response_mock._content = b"{}"
        stream = source_okta.streams(config=oauth_config)[0]
        response_action = get_retriever(stream).requester.error_handler.interpret_response(response_mock).response_action
        assert (response_action in (ResponseAction.RETRY, ResponseAction.RATE_LIMITED)) == should_retry


class TestOktaStream:
    def test_okta_stream_request_params(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("custom_roles", config=oauth_config)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {}
        assert get_retriever(stream).requester.get_request_params(**inputs) == expected_params

    def test_okta_stream_backoff_time(self, url_base, start_date, oauth_config):
        response_mock = requests.Response()
        response_mock.status_code = 429
        stream = get_stream_by_name("custom_roles", config=oauth_config)
        expected_backoff_time = 60.0
        assert get_backoff_time(stream, response_mock) == expected_backoff_time

    def test_okta_stream_incremental_request_params(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("logs", config=oauth_config)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        assert list(get_retriever(stream).requester.get_request_params(**inputs).keys())[0] == "since"

    def test_incremental_okta_stream_backoff_time(self, oauth_config, url_base, start_date):
        response_mock = requests.Response()
        response_mock.status_code = 501
        stream = get_stream_by_name("users", config=oauth_config)
        expected_backoff_time = 60.0
        assert get_backoff_time(stream, response_mock) == expected_backoff_time

    def test_okta_stream_incremental_back_off_now(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        response = requests.Response()
        response.status_code = requests.codes.TOO_MANY_REQUESTS
        response.headers = {"x-rate-limit-reset": int(time.time()) + 130}
        expected_params = (60, 120)
        inputs = {"response": response}
        backoff_time = get_backoff_time(stream, **inputs)
        assert expected_params[0] <= backoff_time <= expected_params[1]

    def test_okta_stream_http_method(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        expected_method = "GET"
        assert get_retriever(stream).requester.http_method.value == expected_method


class TestNextPageToken:
    def test_next_page_token(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}?param1=test_value1&param2=test_value2"}}
        response.headers = {}
        inputs = {"response": response}
        expected_token = {"next_page_token": "https://test_domain.okta.com?param1=test_value1&param2=test_value2"}
        result = get_next_page_token(stream, **inputs)
        assert result == expected_token

    def test_next_page_token_empty_params(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}"}}
        response.headers = {}
        inputs = {"response": response}
        expected_token = {"next_page_token": "https://test_domain.okta.com"}
        result = get_next_page_token(stream, **inputs)
        assert result == expected_token

    def test_next_page_token_link_have_self_and_equal_next(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}"}, "self": {"url": f"{api_url}"}}
        response.headers = {}
        inputs = {"response": response}
        expected_token = None
        result = get_next_page_token(stream, **inputs)
        assert result == expected_token
