# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


CLOUD_ID = "12345678-1234-1234-1234-123456789abc"

_TENANT_INFO_RESPONSE = json.dumps({"cloudId": CLOUD_ID}).encode()


def _source_with_config(config):
    return YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH))


def _stream(config, stream_name):
    for stream in _source_with_config(config).streams(config):
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def _mock_tenant_info(payload=_TENANT_INFO_RESPONSE):
    """Return a context-manager mock for `urllib.request.urlopen`."""
    resp = MagicMock()
    resp.read.return_value = payload
    resp.__enter__ = lambda s: BytesIO(payload)
    resp.__exit__ = lambda s, *a: None
    return patch("components.urllib.request.urlopen", return_value=resp)


@pytest.mark.parametrize(
    "credentials,stream_name,expected_url_base,expected_authenticator,expected_token,mock_tenant_info",
    [
        pytest.param(
            {
                "auth_type": "API Token",
                "api_token": "token",
                "email": "email@email.com",
            },
            "application_roles",
            "https://airbyteio.atlassian.net/rest/api/3/",
            "BasicHttpAuthenticator",
            "Basic ZW1haWxAZW1haWwuY29tOnRva2Vu",
            False,
            id="api_token_rest_v3_domain_route",
        ),
        pytest.param(
            {
                "auth_type": "Service Account",
                "service_account_token": "token",
            },
            "application_roles",
            f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3/",
            "JiraServiceAccountAuthenticator",
            None,
            True,
            id="service_account_auto_cloud_id_rest_v3",
        ),
        pytest.param(
            {
                "auth_type": "OAuth2.0",
                "client_id": "client-id",
                "client_secret": "client-secret",
                "refresh_token": "refresh-token",
                "cloud_id": CLOUD_ID,
            },
            "application_roles",
            f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3/",
            "JiraOAuthAuthenticator",
            None,
            False,
            id="oauth_rest_v3_gateway_route",
        ),
        pytest.param(
            {
                "auth_type": "API Token",
                "api_token": "token",
                "email": "email@email.com",
            },
            "boards",
            "https://airbyteio.atlassian.net/rest/agile/1.0/",
            "BasicHttpAuthenticator",
            "Basic ZW1haWxAZW1haWwuY29tOnRva2Vu",
            False,
            id="api_token_agile_v1_domain_route",
        ),
        pytest.param(
            {
                "auth_type": "Service Account",
                "service_account_token": "token",
            },
            "boards",
            f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/agile/1.0/",
            "JiraServiceAccountAuthenticator",
            None,
            True,
            id="service_account_auto_cloud_id_agile_v1",
        ),
        pytest.param(
            {
                "auth_type": "OAuth2.0",
                "client_id": "client-id",
                "client_secret": "client-secret",
                "refresh_token": "refresh-token",
                "cloud_id": CLOUD_ID,
            },
            "boards",
            f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/agile/1.0/",
            "JiraOAuthAuthenticator",
            None,
            False,
            id="oauth_agile_v1_gateway_route",
        ),
    ],
)
def test_url_routing_by_credential_type(
    config, credentials, stream_name, expected_url_base, expected_authenticator, expected_token, mock_tenant_info
):
    test_config = deepcopy(config)
    test_config["credentials"] = credentials

    if mock_tenant_info:
        with _mock_tenant_info():
            stream = _stream(test_config, stream_name)
    else:
        stream = _stream(test_config, stream_name)

    assert stream.retriever.requester.get_url_base() == expected_url_base
    authenticator = stream.retriever.requester._authenticator
    assert type(authenticator).__name__ == expected_authenticator
    if expected_token:
        assert authenticator.token == expected_token
