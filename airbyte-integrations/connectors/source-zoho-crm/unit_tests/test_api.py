#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock

import pytest
import requests
from source_zoho_crm.api import ZohoAPI


@pytest.fixture
def config():
    return {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
        "dc_region": "US",
        "environment": "Developer",
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


@pytest.mark.parametrize(
    ("edition", "expected_concurrency"),
    (
        ("free", 5),
        ("standard", 10),
        ("professional", 15),
        ("enterprise", 20),
        ("ultimate", 25),
        ("Enterprise", 20),
    ),
)
def test_max_concurrent_requests_detects_edition(mocker, request_mocker, config, edition, expected_concurrency):
    request = request_mocker(content=json.dumps({"org": [{"license_details": {"paid": True, "paid_type": edition}}]}).encode())
    mock_request(mocker, request)
    api = ZohoAPI(config)

    assert api.max_concurrent_requests == expected_concurrency
    if edition == "Enterprise":
        assert api._detect_edition() == "Enterprise"


def test_max_concurrent_requests_detects_trial_edition(mocker, request_mocker, config):
    mock_request(
        mocker,
        request_mocker(
            content=json.dumps({"org": [{"license_details": {"paid": False, "paid_type": None, "trial_type": "enterprise"}}]}).encode()
        ),
    )
    api = ZohoAPI(config)

    assert api.max_concurrent_requests == 20


def test_max_concurrent_requests_defaults_to_free_without_paid_type(mocker, request_mocker, config):
    mock_request(
        mocker,
        request_mocker(content=json.dumps({"org": [{"license_details": {"paid": False, "paid_type": None, "trial_type": None}}]}).encode()),
    )
    api = ZohoAPI(config)

    assert api.max_concurrent_requests == 5
    assert api._detect_edition() == "Free"


@pytest.mark.parametrize(
    "content",
    (
        json.dumps({"org": [{"license_details": {"paid": True, "paid_type": "platinum"}}]}).encode(),
        json.dumps({"org": [{}]}).encode(),
        json.dumps({"org": []}).encode(),
        b"not json",
    ),
)
def test_max_concurrent_requests_defaults_on_unrecognized_org_response(mocker, request_mocker, config, content):
    mock_request(mocker, request_mocker(content=content))
    api = ZohoAPI(config)

    assert api.max_concurrent_requests == 5


def test_max_concurrent_requests_defaults_on_http_error(mocker, request_mocker, config):
    mock_request(mocker, request_mocker(status=401, content=b'{"code":"OAUTH_SCOPE_MISMATCH"}'))
    api = ZohoAPI(config)

    assert api.max_concurrent_requests == 5


def test_max_concurrent_requests_defaults_on_request_exception(mocker, config):
    mocker.patch("source_zoho_crm.api.requests.get", Mock(side_effect=requests.exceptions.ConnectionError("boom")))
    mocker.patch("source_zoho_crm.api.ZohoOauth2Authenticator.get_auth_header", Mock(return_value={}))
    api = ZohoAPI(config)

    assert api.max_concurrent_requests == 5


def test_max_concurrent_requests_caches_successful_detection(mocker, request_mocker, config):
    request = request_mocker(content=json.dumps({"org": [{"license_details": {"paid": True, "paid_type": "enterprise"}}]}).encode())
    mock_request(mocker, request)
    api = ZohoAPI(config)

    assert api.max_concurrent_requests == 20
    assert api.max_concurrent_requests == 20
    assert request.call_count == 1


def test_max_concurrent_requests_caches_fallback(mocker, request_mocker, config):
    request = request_mocker(status=401, content=b'{"code":"OAUTH_SCOPE_MISMATCH"}')
    mock_request(mocker, request)
    api = ZohoAPI(config)

    assert api.max_concurrent_requests == 5
    assert api.max_concurrent_requests == 5
    assert request.call_count == 1
