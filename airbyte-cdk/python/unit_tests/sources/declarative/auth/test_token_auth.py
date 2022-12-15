#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
import requests
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator, BasicHttpAuthenticator, BearerAuthenticator
from requests import Response

LOGGER = logging.getLogger(__name__)

resp = Response()
config = {"username": "user", "password": "password", "header": "header"}
options = {"username": "user", "password": "password", "header": "header"}


@pytest.mark.parametrize(
    "test_name, token, expected_header_value",
    [
        ("test_static_token", "test-token", "Bearer test-token"),
        ("test_token_from_config", "{{ config.username }}", "Bearer user"),
        ("test_token_from_options", "{{ options.username }}", "Bearer user"),
    ],
)
def test_bearer_token_authenticator(test_name, token, expected_header_value):
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = BearerAuthenticator(token, config, options=options)
    header1 = token_auth.get_auth_header()
    header2 = token_auth.get_auth_header()

    prepared_request = requests.PreparedRequest()
    prepared_request.headers = {}
    token_auth(prepared_request)

    assert {"Authorization": expected_header_value} == prepared_request.headers
    assert {"Authorization": expected_header_value} == header1
    assert {"Authorization": expected_header_value} == header2


@pytest.mark.parametrize(
    "test_name, username, password, expected_header_value",
    [
        ("test_static_creds", "user", "password", "Basic dXNlcjpwYXNzd29yZA=="),
        ("test_creds_from_config", "{{ config.username }}", "{{ config.password }}", "Basic dXNlcjpwYXNzd29yZA=="),
        ("test_creds_from_options", "{{ options.username }}", "{{ options.password }}", "Basic dXNlcjpwYXNzd29yZA=="),
    ],
)
def test_basic_authenticator(test_name, username, password, expected_header_value):
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = BasicHttpAuthenticator(username=username, password=password, config=config, options=options)
    header1 = token_auth.get_auth_header()
    header2 = token_auth.get_auth_header()

    prepared_request = requests.PreparedRequest()
    prepared_request.headers = {}
    token_auth(prepared_request)

    assert {"Authorization": expected_header_value} == prepared_request.headers
    assert {"Authorization": expected_header_value} == header1
    assert {"Authorization": expected_header_value} == header2


@pytest.mark.parametrize(
    "test_name, header, token, expected_header, expected_header_value",
    [
        ("test_static_token", "Authorization", "test-token", "Authorization", "test-token"),
        ("test_token_from_config", "{{ config.header }}", "{{ config.username }}", "header", "user"),
        ("test_token_from_options", "{{ options.header }}", "{{ options.username }}", "header", "user"),
    ],
)
def test_api_key_authenticator(test_name, header, token, expected_header, expected_header_value):
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = ApiKeyAuthenticator(header=header, api_token=token, config=config, options=options)
    header1 = token_auth.get_auth_header()
    header2 = token_auth.get_auth_header()

    prepared_request = requests.PreparedRequest()
    prepared_request.headers = {}
    token_auth(prepared_request)

    assert {expected_header: expected_header_value} == prepared_request.headers
    assert {expected_header: expected_header_value} == header1
    assert {expected_header: expected_header_value} == header2
