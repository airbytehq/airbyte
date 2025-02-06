#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from source_zoho_crm.api import ZohoAPI


@pytest.fixture
def config():
    return {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
        "dc_region": "US",
        "environment": "Developer",
        "edition": "Free",
    }


def test_cached_authenticator(config):
    api = ZohoAPI(config)
    # guarantee that each call to API won't lead to refreshing a token every time
    assert api.authenticator is api.authenticator


@pytest.mark.parametrize(
    ("region", "environment", "expected_result"),
    (
        ("US", "Developer", "https://developer.zohoapis.com"),
        ("US", "Production", "https://zohoapis.com"),
        ("US", "Sandbox", "https://sandbox.zohoapis.com"),
        ("AU", "Developer", "https://developer.zohoapis.com.au"),
        ("IN", "Production", "https://zohoapis.in"),
        ("CN", "Sandbox", "https://sandbox.zohoapis.com.cn"),
    ),
)
def test_api_url(config, region, environment, expected_result):
    config["dc_region"] = region
    config["environment"] = environment
    api = ZohoAPI(config)
    assert api.api_url == expected_result


def mock_request(mocker, request):
    mocker.patch("source_zoho_crm.api.requests.get", request)
    mocker.patch("source_zoho_crm.api.ZohoOauth2Authenticator.get_auth_header", Mock(return_value={}))


def test_check_connection_success(mocker, request_mocker, config):
    mock_request(mocker, request_mocker(content=b'{"access_token": "token", "expires_in": 3600}'))
    api = ZohoAPI(config)
    assert api.check_connection() == (True, None)


def test_check_connection_fail(mocker, request_mocker, config):
    mock_request(mocker, request_mocker(status=401, content=b"Authentication failure"))
    api = ZohoAPI(config)
    assert api.check_connection() == (False, b"Authentication failure")


def test_json_from_path_success(mocker, request_mocker, config):
    mock_request(mocker, request_mocker(content=b'{"fields": ["a", "b"], "modules": []}'))
    api = ZohoAPI(config)
    assert api._json_from_path("/fields", "fields") == ["a", "b"]


def test_json_from_path_fail(mocker, request_mocker, config):
    mock_request(mocker, request_mocker(status=204, content=b"No content"))
    api = ZohoAPI(config)
    assert api._json_from_path("/fields", "fields") == []
