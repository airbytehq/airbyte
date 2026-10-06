# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64

import pytest
from conftest import base_config, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
_TOKEN_REQUEST_BODY = "grant_type=refresh_token&refresh_token=test-refresh-token"
_ADS_URL = "https://ads-api.reddit.com/api/v3/ad_accounts/a2_abc123/ads"
_FALLBACK_USER_AGENT = "airbyte:source-reddit-ads:v1"


def _read_ads_with_config(config):
    catalog = CatalogBuilder().with_stream("ad", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY),
            HttpResponse(body='{"access_token":"test-access-token","expires_in":3600}', status_code=200),
        )
        http_mocker.get(HttpRequest(_ADS_URL), HttpResponse(body='{"data":[]}', status_code=200))
        output = read(get_source(config, catalog), config, catalog)
    return output, http_mocker


def _token_request_headers(http_mocker):
    token_requests = [request for request in http_mocker._mocker.request_history if request.method == "POST" and request.url == _TOKEN_URL]
    assert len(token_requests) == 1
    return token_requests[0].headers


def test_spec_keeps_flat_schema_and_makes_user_agent_optional() -> None:
    source = get_source()
    spec = source.resolved_manifest["spec"]
    connection_specification = spec["connection_specification"]

    assert "user_agent" not in connection_specification["required"]
    for field in ("client_id", "client_secret", "refresh_token", "ad_account_id"):
        assert field in connection_specification["required"]
    assert "user_agent" in connection_specification["properties"]
    assert "oneOf" not in connection_specification
    assert "credentials" not in connection_specification["properties"]

    advanced_auth = spec["advanced_auth"]
    assert advanced_auth["auth_flow_type"] == "oauth2.0"
    oauth_config = advanced_auth["oauth_config_specification"]
    authorization = oauth_config["oauth_connector_input_specification"]["access_token_headers"]["Authorization"]
    assert "| b64encode" in authorization
    assert "base64encode" not in authorization
    output_properties = oauth_config["complete_oauth_output_specification"]["properties"]
    assert output_properties["refresh_token"]["path_in_connector_config"] == ["refresh_token"]
    server_output_properties = oauth_config["complete_oauth_server_output_specification"]["properties"]
    assert server_output_properties["client_id"]["path_in_connector_config"] == ["client_id"]
    assert server_output_properties["client_secret"]["path_in_connector_config"] == ["client_secret"]


def test_manifest_has_no_oneof_anywhere_in_connection_specification() -> None:
    import yaml

    manifest = get_source().resolved_manifest
    assert "oneOf" not in yaml.safe_dump(manifest["spec"]["connection_specification"])


@pytest.mark.parametrize("missing_or_empty", ["missing", "empty"])
def test_token_refresh_falls_back_to_airbyte_user_agent(missing_or_empty: str) -> None:
    config = base_config()
    if missing_or_empty == "missing":
        del config["user_agent"]
    else:
        config["user_agent"] = ""

    output, http_mocker = _read_ads_with_config(config)

    assert output.errors == []
    headers = _token_request_headers(http_mocker)
    assert headers["User-Agent"] == _FALLBACK_USER_AGENT
    expected_basic = base64.b64encode(b"test-client-id:test-client-secret").decode()
    assert headers["Authorization"] == f"Basic {expected_basic}"


def test_token_refresh_sends_configured_user_agent() -> None:
    output, http_mocker = _read_ads_with_config(base_config())

    assert output.errors == []
    headers = _token_request_headers(http_mocker)
    assert headers["User-Agent"] == "airbyte:reddit-ads-sync:v1.0 (by /u/airbyte)"
    expected_basic = base64.b64encode(b"test-client-id:test-client-secret").decode()
    assert headers["Authorization"] == f"Basic {expected_basic}"
