# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import pytest
from source_salesforce.api import API_VERSION
from source_salesforce.source import SourceSalesforce

from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType
from airbyte_cdk.utils import AirbyteTracedException


@pytest.mark.parametrize("is_sandbox", [False, True])
@pytest.mark.parametrize(
    "response,hint",
    [
        ({"error": "invalid_grant", "error_description": "revoked refresh token"}, "Re-authenticate the source"),
        ({"error": "invalid_grant"}, "test.salesforce.com"),
        ({"error": "invalid_client_id", "error_description": "client identifier invalid"}, "client ID and client secret"),
        ({"error": "invalid_client", "error_description": "invalid client credentials"}, "Connected App credentials"),
        ({"error": "API_DISABLED_FOR_ORG"}, '"API Enabled"'),
        ({"error": "unknown", "error_description": "API is not enabled for this Organization or Partner"}, "API-supported edition"),
        ({"error": "invalid_grant", "error_description": "ip restricted"}, "Allowlist Airbyte IPs"),
        ({"error": "invalid_grant", "error_description": "Login from restricted IP"}, "IP Relaxation"),
        ({"error": "LOGIN_MUST_USE_SECURITY_TOKEN"}, "Allowlist Airbyte IPs"),
        ({"error": "invalid_grant", "error_description": "LOGIN_MUST_USE_SECURITY_TOKEN"}, "IP Relaxation"),
        ({"error": "unknown", "error_description": "Authentication failure."}, "is_sandbox"),
        ({"error": "invalid_client", "error_description": None}, "client ID and client secret"),
        ({"error": "unknown", "error_description": "sensitive-response-value"}, "Salesforce login failed"),
        ({}, "Salesforce login failed"),
    ],
)
def test_connection_check_login_failures(requests_mock, stream_config, is_sandbox, response, hint):
    config = {**stream_config, "is_sandbox": is_sandbox}
    source = SourceSalesforce(ConfiguredAirbyteCatalog(streams=[]), config, None)
    login_url = f"https://{'test' if is_sandbox else 'login'}.salesforce.com/services/oauth2/token"
    requests_mock.post(login_url, json=response, status_code=400)

    with pytest.raises(AirbyteTracedException) as raised:
        source.check_connection(logging.getLogger("airbyte"), config)

    assert raised.value.failure_type == FailureType.config_error
    assert hint in raised.value.message
    assert "sensitive-response-value" not in raised.value.message
    assert len(raised.value.message) <= 200
    assert requests_mock.call_count == 1


@pytest.mark.parametrize(
    "error",
    [
        {"errorCode": "API_DISABLED_FOR_ORG", "message": "API access unavailable"},
        {"errorCode": "FORBIDDEN", "message": "API is not enabled for this Organization"},
    ],
)
def test_connection_check_reports_api_disabled_after_login(requests_mock, stream_config, error):
    source = SourceSalesforce(ConfiguredAirbyteCatalog(streams=[]), stream_config, None)
    requests_mock.post(
        "https://login.salesforce.com/services/oauth2/token",
        json={"access_token": "fake-token", "instance_url": "https://fake.salesforce.com"},
    )
    requests_mock.get(f"https://fake.salesforce.com/services/data/{API_VERSION}/sobjects", json=[error], status_code=403)

    with pytest.raises(AirbyteTracedException) as raised:
        source.check_connection(logging.getLogger("airbyte"), stream_config)

    assert raised.value.failure_type == FailureType.config_error
    assert '"API Enabled"' in raised.value.message
    assert "API-supported edition" in raised.value.message


def test_connection_check_succeeds_after_login(requests_mock, stream_config):
    source = SourceSalesforce(ConfiguredAirbyteCatalog(streams=[]), stream_config, None)
    requests_mock.post(
        "https://login.salesforce.com/services/oauth2/token",
        json={"access_token": "fake-token", "instance_url": "https://fake.salesforce.com"},
    )
    requests_mock.get(f"https://fake.salesforce.com/services/data/{API_VERSION}/sobjects", json={"sobjects": []})
    assert source.check_connection(logging.getLogger("airbyte"), stream_config) == (True, None)
