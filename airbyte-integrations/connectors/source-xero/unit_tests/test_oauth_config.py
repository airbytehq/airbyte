#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pathlib

import pytest
import yaml


MANIFEST_PATH = pathlib.Path(__file__).resolve().parents[1] / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _get_spec(manifest):
    return manifest["spec"]["connection_specification"]


def _get_advanced_auth(manifest):
    return manifest["spec"]["advanced_auth"]


def _get_authenticators(manifest):
    return manifest["definitions"]["base_requester"]["authenticator"]["authenticators"]


@pytest.mark.parametrize(
    "auth_type,expected_title,expected_required",
    [
        pytest.param(
            "oauth2_authorization_code",
            "Authenticate via Xero (OAuth)",
            ["auth_type", "client_id", "client_secret", "refresh_token"],
            id="oauth2_authorization_code",
        ),
        pytest.param(
            "oauth2_confidential_application",
            "OAuth Custom Connection",
            ["auth_type", "client_id", "client_secret"],
            id="oauth2_confidential_application",
        ),
        pytest.param(
            "oauth2_access_token",
            "Bearer Access Token",
            ["access_token", "auth_type"],
            id="oauth2_access_token",
        ),
    ],
)
def test_spec_credentials_oneof_contains_auth_type(manifest, auth_type, expected_title, expected_required):
    credentials = _get_spec(manifest)["properties"]["credentials"]
    matching = [
        opt for opt in credentials["oneOf"]
        if opt["properties"]["auth_type"].get("const") == auth_type
    ]
    assert len(matching) == 1, f"Expected exactly one oneOf entry for {auth_type}"
    option = matching[0]
    assert option["title"] == expected_title
    assert sorted(option["required"]) == sorted(expected_required)


def test_oauth2_authorization_code_secrets_are_marked(manifest):
    credentials = _get_spec(manifest)["properties"]["credentials"]
    oauth_option = [
        opt for opt in credentials["oneOf"]
        if opt["properties"]["auth_type"].get("const") == "oauth2_authorization_code"
    ][0]
    for secret_field in ("client_id", "client_secret", "refresh_token"):
        assert oauth_option["properties"][secret_field].get("airbyte_secret") is True, (
            f"{secret_field} must be marked airbyte_secret"
        )


def test_selective_authenticator_has_oauth2_authorization_code_branch(manifest):
    authenticators = _get_authenticators(manifest)
    assert "oauth2_authorization_code" in authenticators
    branch = authenticators["oauth2_authorization_code"]
    assert branch["type"] == "OAuthAuthenticator"
    assert branch["token_refresh_endpoint"] == "https://identity.xero.com/connect/token"
    assert branch["grant_type"] == "refresh_token"


def test_advanced_auth_block_configured(manifest):
    advanced_auth = _get_advanced_auth(manifest)
    assert advanced_auth["auth_flow_type"] == "oauth2.0"
    assert advanced_auth["predicate_key"] == ["credentials", "auth_type"]
    assert advanced_auth["predicate_value"] == "oauth2_authorization_code"

    oauth_spec = advanced_auth["oauth_config_specification"]
    input_spec = oauth_spec["oauth_connector_input_specification"]
    assert "login.xero.com" in input_spec["consent_url"]
    assert input_spec["access_token_url"] == "https://identity.xero.com/connect/token"
    scope_values = [s["scope"] for s in input_spec["scopes"]]
    assert "offline_access" in scope_values
    assert "refresh_token" in input_spec["extract_output"]

    output_spec = oauth_spec["complete_oauth_output_specification"]
    assert output_spec["properties"]["refresh_token"]["path_in_connector_config"] == [
        "credentials",
        "refresh_token",
    ]
