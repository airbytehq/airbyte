# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import time
from datetime import datetime
from unittest.mock import patch

import pytest
import requests
import requests_mock


@pytest.fixture
def mock_authenticator(components_module):
    PayPalOauth2Authenticator = components_module.PayPalOauth2Authenticator
    return PayPalOauth2Authenticator(
        config={},
        parameters={},
        client_id="test_client_id",
        client_secret="test_client_secret",
        token_refresh_endpoint="https://test.token.endpoint",
        grant_type="test_grant_type",
    )


def test_get_refresh_access_token_response(mock_authenticator):
    expected_response_json = {"access_token": "test_access_token", "expires_in": 3600}
    with requests_mock.Mocker() as mock_request:
        mock_request.post("https://test.token.endpoint", json=expected_response_json, status_code=200)
        # Call _get_refresh method
        mock_authenticator._get_refresh_access_token_response()

        assert mock_authenticator.access_token == expected_response_json["access_token"]


def test_token_expiration(mock_authenticator):
    # Mock response for initial token request
    initial_response_json = {"access_token": "initial_access_token", "expires_in": 1}
    # Mock response for token refresh request
    refresh_response_json = {"access_token": "refreshed_access_token", "expires_in": 3600}
    with requests_mock.Mocker() as mock_request:
        mock_request.post("https://test.token.endpoint", json=initial_response_json, status_code=200)
        mock_authenticator._get_refresh_access_token_response()

        # Assert that the initial access token is set correctly
        assert mock_authenticator.access_token == initial_response_json["access_token"]
        time.sleep(2)

        mock_request.post("https://test.token.endpoint", json=refresh_response_json, status_code=200)
        mock_authenticator._get_refresh_access_token_response()

        # Assert that the access token is refreshed
        assert mock_authenticator.access_token == refresh_response_json["access_token"]


def test_backoff_retry(mock_authenticator, caplog):
    mock_response = {"access_token": "test_access_token", "expires_in": 3600}
    mock_reason = "Too Many Requests"

    with requests_mock.Mocker() as mock_request:
        mock_request.post("https://test.token.endpoint", json=mock_response, status_code=429, reason=mock_reason)
        with caplog.at_level(logging.INFO):
            try:
                mock_authenticator._get_refresh_access_token_response()
            except requests.exceptions.HTTPError:
                pass  # Ignore the HTTPError
            else:
                pytest.fail("Expected DefaultBackoffException to be raised")


@pytest.fixture
def authenticator_parameters():
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "config": {},
        "parameters": {},
        "token_refresh_endpoint": "https://test.token.endpoint",
        "grant_type": "test_grant_type",
    }


def test_get_headers(components_module, authenticator_parameters):
    PayPalOauth2Authenticator = components_module.PayPalOauth2Authenticator
    expected_basic_auth = "Basic dGVzdF9jbGllbnRfaWQ6dGVzdF9jbGllbnRfc2VjcmV0"
    authenticator = PayPalOauth2Authenticator(**authenticator_parameters)
    headers = authenticator.get_headers()
    assert headers == {"Authorization": expected_basic_auth}


@pytest.fixture(name="config")
def config_fixture():
    # From File test
    # with open('../secrets/config.json') as f:
    #     return json.load(f)
    # Mock test
    return {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "start_date": "2024-01-30T00:00:00Z",
        "end_date": "2024-02-01T00:00:00Z",
        "dispute_start_date": "2024-02-01T00:00:00.000Z",
        "dispute_end_date": "2024-02-05T23:59:00.000Z",
        "buyer_username": "Your Buyer email",
        "buyer_password": "Your Buyer Password",
        "payer_id": "ypur ACCOUNT ID",
        "is_sandbox": True,
    }


@pytest.fixture(name="source")
def source_fixture(components_module):
    SourcePaypalTransaction = components_module.SourcePaypalTransaction
    return SourcePaypalTransaction()


def validate_date_format(date_str, format):
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def test_date_formats_in_config(config):
    start_date_format = "%Y-%m-%dT%H:%M:%SZ"
    dispute_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    assert validate_date_format(config["start_date"], start_date_format), "Start date format is incorrect"
    assert validate_date_format(config["end_date"], start_date_format), "End date format is incorrect"
    assert validate_date_format(config["dispute_start_date"], dispute_date_format), "Dispute start date format is incorrect"
    assert validate_date_format(config["dispute_end_date"], dispute_date_format), "Dispute end date format is incorrect"


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_paypal_transactions.source.AirbyteLogger")
