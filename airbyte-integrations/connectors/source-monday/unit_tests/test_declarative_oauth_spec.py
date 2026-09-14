# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_SPEC = YamlDeclarativeSource(config={}, catalog=None, state=None, path_to_yaml=_MANIFEST_PATH).spec(logging.getLogger("airbyte"))
_OAUTH_CONFIG_SPECIFICATION = _SPEC.advanced_auth.oauth_config_specification


def test_oauth_connector_input_specification_declares_pkce_flow():
    connector_input = _OAUTH_CONFIG_SPECIFICATION.oauth_connector_input_specification

    assert connector_input.consent_url.startswith("https://auth.monday.com/oauth2/authorize?")
    assert "code_challenge={{ state_value | codechallengeS256 }}" in connector_input.consent_url
    assert "code_challenge_method=S256" in connector_input.consent_url
    assert 43 <= connector_input.state.min <= connector_input.state.max <= 128
    assert connector_input.access_token_url == "https://auth.monday.com/oauth_ms/oauth/token"
    assert connector_input.access_token_params["grant_type"] == "authorization_code"
    assert connector_input.access_token_params["code_verifier"] == "{{ state_value }}"
    assert connector_input.extract_output == ["access_token", "refresh_token"]


def test_oauth_output_is_persisted_into_credentials():
    output_properties = _OAUTH_CONFIG_SPECIFICATION.complete_oauth_output_specification["properties"]

    assert set(output_properties) == {"access_token", "refresh_token"}
    for name, definition in output_properties.items():
        assert definition["path_in_connector_config"] == ["credentials", name]

    oauth_option = next(
        option for option in _SPEC.connectionSpecification["properties"]["credentials"]["oneOf"] if option["title"] == "OAuth2.0"
    )
    assert "refresh_token" in oauth_option["required"]
