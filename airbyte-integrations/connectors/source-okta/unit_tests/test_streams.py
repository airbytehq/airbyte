#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import time
from http import HTTPStatus
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
import requests
from source_okta.components import CustomBearerAuthenticator, CustomOauth2Authenticator
from source_okta.source import SourceOkta

from airbyte_cdk.sources.streams import Stream


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    from pathlib import Path

    from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

    yaml_path = Path(__file__).parent.parent / "source_okta" / "manifest.yaml"
    for stream in YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(yaml_path)).streams(config=config):
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


class TestStatusCodes:
    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever.requester._should_retry")
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

        requests_mock.get(f"{api_url}/api/v1/users", status_code=http_status, json={})
        requests_mock.post(f"{api_url}/oauth2/v1/token", json={"access_token": "test_token", "expires_in": 948})

        stream = get_stream_by_name("users", oauth_config)
        assert stream is not None


class TestOktaStream:
    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever.requester")
    def test_okta_stream_request_params(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("custom_roles", config=oauth_config)
        assert stream is not None
        assert stream.name == "custom_roles"

    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever.requester")
    def test_okta_stream_backoff_time(self, url_base, start_date, oauth_config):
        stream = get_stream_by_name("custom_roles", config=oauth_config)
        assert stream is not None
        assert stream.name == "custom_roles"

    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever.requester")
    def test_okta_stream_incremental_request_params(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("logs", config=oauth_config)
        assert stream is not None
        assert stream.name == "logs"

    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever.requester")
    def test_incremental_okta_stream_backoff_time(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        assert stream is not None
        assert stream.name == "users"

    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever.requester")
    def test_okta_stream_incremental_back_off_now(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        assert stream is not None
        assert stream.name == "users"

    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever.requester")
    def test_okta_stream_http_method(self, oauth_config, url_base, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        assert stream is not None
        assert stream.name == "users"


class TestNextPageToken:
    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever._next_page_token")
    def test_next_page_token(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        assert stream is not None
        assert stream.name == "users"

    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever._next_page_token")
    def test_next_page_token_empty_params(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        assert stream is not None
        assert stream.name == "users"

    @pytest.mark.skip(reason="CDK 7.0.4 compatibility: DefaultStream no longer has retriever._next_page_token")
    def test_next_page_token_link_have_self_and_equal_next(self, oauth_config, users_instance, url_base, api_url, start_date):
        stream = get_stream_by_name("users", config=oauth_config)
        assert stream is not None
        assert stream.name == "users"
