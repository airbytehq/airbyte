# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition, AddFields


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


@patch("requests.request")
def test_get_refresh_access_token_response(mock_request, mock_authenticator):
    expected_response_json = {"access_token": "test_access_token", "expires_in": 3600}

    mock_response = MagicMock()
    mock_response.json.return_value = expected_response_json
    mock_response.status_code = 200
    mock_request.return_value = mock_response

    # Call _get_refresh method
    mock_authenticator._get_refresh_access_token_response()

    assert mock_authenticator.access_token == expected_response_json["access_token"]


@patch("requests.request")
def test_token_expiration(mock_request, mock_authenticator):
    # Mock response for initial token request
    initial_response_json = {"access_token": "initial_access_token", "expires_in": 1}
    # Mock response for token refresh request
    refresh_response_json = {"access_token": "refreshed_access_token", "expires_in": 3600}

    mock_response_initial = MagicMock()
    mock_response_initial.json.return_value = initial_response_json
    mock_response_initial.status_code = 200

    mock_response_refresh = MagicMock()
    mock_response_refresh.json.return_value = refresh_response_json
    mock_response_refresh.status_code = 200

    mock_request.side_effect = [mock_response_initial, mock_response_refresh]
    mock_authenticator._get_refresh_access_token_response()

    # Assert that the initial access token is set correctly
    assert mock_authenticator.access_token == initial_response_json["access_token"]
    time.sleep(2)

    mock_authenticator._get_refresh_access_token_response()

    # Assert that the access token is refreshed
    assert mock_authenticator.access_token == refresh_response_json["access_token"]


@patch("requests.request")
def test_backoff_retry(mock_request, mock_authenticator, caplog):
    mock_response = {"access_token": "test_access_token", "expires_in": 3600}
    mock_reason = "Too Many Requests"

    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429
    mock_response_429.reason = mock_reason
    mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError()

    mock_response_success = MagicMock()
    mock_response_success.json.return_value = mock_response
    mock_response_success.status_code = 200

    mock_request.side_effect = [mock_response_429, mock_response_success]
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
    headers = authenticator.get_refresh_request_headers()
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


@pytest.fixture(name="manifest")
def manifest_fixture():
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return yaml.safe_load(manifest_path.read_text())


def test_manifest_transaction_id_add_field_is_string(manifest):
    transactions = manifest["definitions"]["streams"]["transactions"]
    transaction_id_fields = [
        field
        for transformation in transactions["transformations"]
        if transformation["type"] == "AddFields"
        for field in transformation["fields"]
        if field["path"] == ["transaction_id"]
    ]

    assert len(transaction_id_fields) == 1
    assert transaction_id_fields[0]["value_type"] == "string"


@pytest.mark.parametrize(
    ("record", "expected_transaction_id"),
    [
        pytest.param(
            {"transaction_info": {"transaction_id": "35E87645934406417"}},
            "35E87645934406417",
            id="scientific-notation-like-id",
        ),
        pytest.param(
            {"transaction_info": {"transaction_id": "1E2"}},
            "1E2",
            id="short-scientific-notation-like-id",
        ),
        pytest.param(
            {"transaction_info": {"transaction_id": "99999999999"}},
            "99999999999",
            id="numeric-string",
        ),
        pytest.param(
            {"transaction_info": {"transaction_id": "ABC123DEF"}},
            "ABC123DEF",
            id="alphanumeric-string",
        ),
        pytest.param({"transaction_info": {}}, "", id="missing-transaction-id"),
    ],
)
def test_transaction_id_add_field_preserves_string_values(record, expected_transaction_id):
    transaction_id_transform = AddFields(
        fields=[
            AddedFieldDefinition(
                path=["transaction_id"],
                value="{{ record['transaction_info']['transaction_id'] }}",
                value_type=str,
                parameters={},
            )
        ],
        parameters={},
    )

    transaction_id_transform.transform(record, config={})

    assert record["transaction_id"] == expected_transaction_id
    assert isinstance(record["transaction_id"], str)
