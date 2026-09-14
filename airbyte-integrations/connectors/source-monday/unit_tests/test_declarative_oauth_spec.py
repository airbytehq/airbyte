# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

import yaml

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_MANIFEST = yaml.safe_load(_MANIFEST_PATH.read_text())
_SPEC = YamlDeclarativeSource(config={}, catalog=None, state=None, path_to_yaml=_MANIFEST_PATH).spec(logging.getLogger("airbyte"))
_OAUTH_CONFIG_SPECIFICATION = _SPEC.advanced_auth.oauth_config_specification


def test_oauth_connector_input_specification_declares_pkce_flow():
    connector_input = _OAUTH_CONFIG_SPECIFICATION.oauth_connector_input_specification

    assert connector_input.consent_url.startswith("https://auth.monday.com/oauth2/authorize?")
    for placeholder in (
        "{{client_id_param}}",
        "{{redirect_uri_param}}",
        "{{scopes_param}}",
        "{{state_param}}",
        "code_challenge={{ state_value | codechallengeS256 }}",
        "code_challenge_method=S256",
        "subdomain={{subdomain}}",
    ):
        assert placeholder in connector_input.consent_url

    assert 43 <= connector_input.state.min <= connector_input.state.max <= 128
    assert connector_input.access_token_url == "https://auth.monday.com/oauth_ms/oauth/token"
    assert connector_input.access_token_headers == {"Content-Type": "application/json"}
    assert connector_input.access_token_params == {
        "grant_type": "authorization_code",
        "code": "{{ auth_code_value }}",
        "client_id": "{{ client_id_value }}",
        "client_secret": "{{ client_secret_value }}",
        "redirect_uri": "{{ redirect_uri_value }}",
        "code_verifier": "{{ state_value }}",
    }
    assert connector_input.extract_output == ["access_token", "refresh_token", "expires_in"]

    # CDK 7.5.0 drops `scopes` when serializing the spec, so it is only observable in the manifest
    manifest_connector_input = _MANIFEST["spec"]["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]
    assert manifest_connector_input["scopes"] == [
        {"scope": scope}
        for scope in (
            "me:read",
            "boards:read",
            "workspaces:read",
            "users:read",
            "account:read",
            "updates:read",
            "assets:read",
            "tags:read",
            "teams:read",
        )
    ]


def test_oauth_output_is_persisted_into_credentials():
    output_properties = _OAUTH_CONFIG_SPECIFICATION.complete_oauth_output_specification["properties"]

    assert set(output_properties) == {"access_token", "refresh_token", "token_expiry_date"}
    for name, definition in output_properties.items():
        assert definition["path_in_connector_config"] == ["credentials", name]

    oauth_option = next(
        option for option in _SPEC.connectionSpecification["properties"]["credentials"]["oneOf"] if option["title"] == "OAuth2.0"
    )
    assert "refresh_token" in oauth_option["required"]
