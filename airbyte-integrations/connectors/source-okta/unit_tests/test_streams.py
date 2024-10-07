#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import time
from http import HTTPStatus
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.streams import Stream
from source_okta.components import CustomBearerAuthenticator, CustomOauth2Authenticator
from source_okta.source import SourceOkta


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceOkta()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


class TestOktaStream:
    def test_okta_stream_request_params(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("custom_roles", config=oauth_config)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {}
        assert stream.retriever.requester.get_request_params(**inputs) == expected_params

    def test_okta_stream_incremental_request_params(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("logs", config=oauth_config)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        assert list(stream.retriever.requester.get_request_params(**inputs).keys())[0] == "since"

    # def test_okta_stream_incremental_back_off_now(self, oauth_config, url_base, start_date):
    #     stream = get_stream_by_name("users", config=oauth_config)
    #     response = requests.Response()
    #     response.status_code = requests.codes.TOO_MANY_REQUESTS
    #     response.headers = {"x-rate-limit-reset": int(time.time()) + 130}
    #     expected_params = (60, 120)
    #     inputs = {"response": response}
    #     get_backoff_time = stream.retriever.requester.error_handler.interpret_response(**inputs)
    #     assert expected_params[0] <= get_backoff_time <= expected_params[1]

    def test_okta_stream_http_method(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        expected_method = "GET"
        assert stream.retriever.requester.http_method.value == expected_method


class TestNextPageToken:
    def test_next_page_token(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}?param1=test_value1&param2=test_value2"}}
        response.headers = {}
        inputs = {"response": response}
        expected_token = {"next_page_token": "https://test_domain.okta.com?param1=test_value1&param2=test_value2"}
        result = stream.retriever._next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_empty_params(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}"}}
        response.headers = {}
        inputs = {"response": response}
        expected_token = {"next_page_token": "https://test_domain.okta.com"}
        result = stream.retriever._next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_link_have_self_and_equal_next(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}"}, "self": {"url": f"{api_url}"}}
        response.headers = {}
        inputs = {"response": response}
        expected_token = None
        result = stream.retriever._next_page_token(**inputs)
        assert result == expected_token
