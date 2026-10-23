# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from urllib.parse import parse_qs

import requests_mock
import yaml
from conftest import MANIFEST_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_MANIFEST = yaml.safe_load(MANIFEST_PATH.read_text())
_SPEC = get_source(config={}).spec(logging.getLogger("airbyte"))
_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


def _oauth_config_specification():
    assert _SPEC.advanced_auth is not None, "spec.advanced_auth must declare the LinkedIn OAuth flow"
    return _SPEC.advanced_auth.oauth_config_specification


def test_advanced_auth_targets_the_default_oauth_option() -> None:
    credentials_options = _SPEC.connectionSpecification["properties"]["credentials"]["oneOf"]
    oauth_option = credentials_options[0]

    assert oauth_option["title"] == "OAuth2.0"
    assert _SPEC.advanced_auth.auth_flow_type.value == "oauth2.0"
    assert _SPEC.advanced_auth.predicate_key == ["credentials", "auth_method"]
    assert _SPEC.advanced_auth.predicate_value == oauth_option["properties"]["auth_method"]["const"]


def test_oauth_connector_input_specification_declares_authorization_code_flow() -> None:
    connector_input = _oauth_config_specification().oauth_connector_input_specification

    assert connector_input.consent_url.startswith("https://www.linkedin.com/oauth/v2/authorization?")
    for placeholder in ("{{client_id_param}}", "{{redirect_uri_param}}", "{{scopes_param}}", "{{state_param}}", "response_type=code"):
        assert placeholder in connector_input.consent_url

    assert connector_input.access_token_url == _TOKEN_URL
    assert connector_input.access_token_headers == {"Content-Type": "application/x-www-form-urlencoded"}
    assert connector_input.access_token_params == {
        "grant_type": "authorization_code",
        "code": "{{ auth_code_value }}",
        "client_id": "{{ client_id_value }}",
        "client_secret": "{{ client_secret_value }}",
        "redirect_uri": "{{ redirect_uri_value }}",
    }
    assert connector_input.extract_output == ["refresh_token"]

    # The CDK drops `scopes` when serializing the spec, so it is only observable in the manifest.
    manifest_connector_input = _MANIFEST["spec"]["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]
    assert manifest_connector_input["scopes"] == [{"scope": "r_organization_social"}, {"scope": "rw_organization_admin"}]


def test_oauth_outputs_map_to_the_fields_the_authenticator_reads() -> None:
    oauth_spec = _oauth_config_specification()
    oauth_option = _SPEC.connectionSpecification["properties"]["credentials"]["oneOf"][0]

    output_properties = oauth_spec.complete_oauth_output_specification["properties"]
    server_output_properties = oauth_spec.complete_oauth_server_output_specification["properties"]
    assert set(oauth_spec.complete_oauth_server_input_specification["properties"]) == {"client_id", "client_secret"}

    persisted = {**output_properties, **server_output_properties}
    assert set(persisted) == {"refresh_token", "client_id", "client_secret"}
    for name, definition in persisted.items():
        assert definition["path_in_connector_config"] == ["credentials", name]
        assert name in oauth_option["properties"]
        assert name in oauth_option["required"]


def test_config_produced_by_oauth_flow_refreshes_token_and_reads() -> None:
    config = {
        "org_id": "12345678",
        "credentials": {
            "auth_method": "oAuth2.0",
            "client_id": "airbyte_client_id",
            "client_secret": "airbyte_client_secret",
            "refresh_token": "cloud_issued_refresh_token",
        },
        "start_date": "2023-10-31T00:00:00Z",
        "time_granularity_type": "DAY",
    }
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "fresh_access_token", "expires_in": 5184000})
        mocker.get("https://api.linkedin.com/rest/organizations/12345678", json={"id": 12345678, "localizedName": "Test Org"})
        catalog = CatalogBuilder().with_stream("organization_lookup", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

        token_requests = [request for request in mocker.request_history if request.url == _TOKEN_URL]
        assert len(token_requests) == 1
        token_body = parse_qs(token_requests[0].text)
        assert token_body["grant_type"] == ["refresh_token"]
        assert token_body["refresh_token"] == ["cloud_issued_refresh_token"]
        assert token_body["client_id"] == ["airbyte_client_id"]
        assert token_body["client_secret"] == ["airbyte_client_secret"]

        api_requests = [request for request in mocker.request_history if request.hostname == "api.linkedin.com"]
        assert api_requests
        assert all(request.headers["Authorization"] == "Bearer fresh_access_token" for request in api_requests)
    assert len(output.records) == 1
