#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.auth.selective_authenticator import SelectiveAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.auth.token_provider import InterpolatedStringTokenProvider
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.models import HttpMethod
from source_mailchimp.components import MailChimpRequester


@pytest.mark.parametrize(
    ["config"],
    [
        [{"credentials": {"auth_type": "apikey", "apikey": "random_api_key-us10"}}],
        [{"credentials": {"auth_type": "oauth2.0", "access_token": "638dcc33169467b72ebc5dd74b529f9e"}}],
    ],
    ids=["test_requester_datacenter_with_api_key", "test_requester_datacenter_with_oauth_flow"],
)
def test_mailchimp_requester(config: dict, requests_mock):
    http_method = HttpMethod.GET
    name = "stream_name"

    basic_http_authenticator = BasicHttpAuthenticator(username="username", password="apikey", config=config, parameters={})

    token_provider = InterpolatedStringTokenProvider(config=config, api_token="test_token", parameters={})
    token_auth = BearerAuthenticator(token_provider, config, parameters={})

    authenticators = {"apikey": basic_http_authenticator, "oauth2.0": token_auth}
    selective_authenticator = SelectiveAuthenticator(
        config=config,
        authenticators=authenticators,
        authenticator_selection_path=["credentials", "auth_type"],
    )

    requester = MailChimpRequester(
        name=name,
        url_base=InterpolatedString.create("https://{{ config['data_center'] }}.api.mailchimp.com/3.0/", parameters={}),
        path=InterpolatedString.create("v1/{{ stream_slice['id'] }}", parameters={}),
        http_method=http_method,
        authenticator=selective_authenticator,
        error_handler=MagicMock(),
        config=config,
        parameters={},
    )
    requests_mock.get("https://login.mailchimp.com/oauth2/metadata", json={"dc": "us10"})
    assert requester.get_url_base() == "https://us10.api.mailchimp.com/3.0/"
