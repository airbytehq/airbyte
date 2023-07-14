#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
import requests
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator, BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from requests import Response

LOGGER = logging.getLogger(__name__)

resp = Response()
config = {"username": "user", "password": "password", "header": "header"}
parameters = {"username": "user", "password": "password", "header": "header"}


@pytest.mark.parametrize(
    "test_name, token, expected_header_value",
    [
        ("test_static_token", "test-token", "Bearer test-token"),
        ("test_token_from_config", "{{ config.username }}", "Bearer user"),
        ("test_token_from_parameters", "{{ parameters.username }}", "Bearer user"),
    ],
)
def test_bearer_token_authenticator(test_name, token, expected_header_value):
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = BearerAuthenticator(token, config, parameters=parameters)
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
        ("test_creds_from_parameters", "{{ parameters.username }}", "{{ parameters.password }}", "Basic dXNlcjpwYXNzd29yZA=="),
    ],
)
def test_basic_authenticator(test_name, username, password, expected_header_value):
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = BasicHttpAuthenticator(username=username, password=password, config=config, parameters=parameters)
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
        ("test_token_from_parameters", "{{ parameters.header }}", "{{ parameters.username }}", "header", "user"),
    ],
)
def test_api_key_authenticator(test_name, header, token, expected_header, expected_header_value):
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = ApiKeyAuthenticator(
        request_option=RequestOption(
            inject_into=RequestOptionType.header,
            field_name=header,
            parameters={}
        ),
        api_token=token,
        config=config,
        parameters=parameters
    )
    header1 = token_auth.get_auth_header()
    header2 = token_auth.get_auth_header()

    prepared_request = requests.PreparedRequest()
    prepared_request.headers = {}
    token_auth(prepared_request)

    assert {expected_header: expected_header_value} == prepared_request.headers
    assert {expected_header: expected_header_value} == header1
    assert {expected_header: expected_header_value} == header2


@pytest.mark.parametrize(
    "test_name, field_name, token, expected_field_name, expected_field_value, inject_type, validation_fn",
    [
        ("test_static_token", "Authorization", "test-token", "Authorization", "test-token", RequestOptionType.request_parameter, "get_request_params"),
        ("test_token_from_config", "{{ config.header }}", "{{ config.username }}", "header", "user", RequestOptionType.request_parameter, "get_request_params"),
        ("test_token_from_parameters", "{{ parameters.header }}", "{{ parameters.username }}", "header", "user", RequestOptionType.request_parameter, "get_request_params"),
        ("test_static_token", "Authorization", "test-token", "Authorization", "test-token", RequestOptionType.body_data, "get_request_body_data"),
        ("test_token_from_config", "{{ config.header }}", "{{ config.username }}", "header", "user", RequestOptionType.body_data, "get_request_body_data"),
        ("test_token_from_parameters", "{{ parameters.header }}", "{{ parameters.username }}", "header", "user", RequestOptionType.body_data, "get_request_body_data"),
        ("test_static_token", "Authorization", "test-token", "Authorization", "test-token", RequestOptionType.body_json, "get_request_body_json"),
        ("test_token_from_config", "{{ config.header }}", "{{ config.username }}", "header", "user", RequestOptionType.body_json, "get_request_body_json"),
        ("test_token_from_parameters", "{{ parameters.header }}", "{{ parameters.username }}", "header", "user", RequestOptionType.body_json, "get_request_body_json"),
    ],
)
def test_api_key_authenticator_inject(test_name, field_name, token, expected_field_name, expected_field_value, inject_type, validation_fn):
    """
    Should match passed in token, no matter how many times token is retrieved.
    """
    token_auth = ApiKeyAuthenticator(
        request_option=RequestOption(
            inject_into=inject_type,
            field_name=field_name,
            parameters={}
        ),
        api_token=token,
        config=config,
        parameters=parameters
    )
    assert {expected_field_name: expected_field_value} == getattr(token_auth, validation_fn)()
