#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import base64
import hashlib
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import jinja2
import pytest
import yaml
from jsonschema import Draft7Validator


SPEC_PATH = Path(__file__).resolve().parents[1] / "source_salesforce" / "spec.yaml"

_CLIENT_CREDENTIALS = {"client_id": "a_client_id", "client_secret": "a_client_secret", "refresh_token": "a_refresh_token"}
_JWT_CREDENTIALS = {"auth_type": "JWT", "client_id": "a_client_id", "username": "a_user", "private_key": "a_private_key"}


def _load_spec():
    with SPEC_PATH.open() as spec_file:
        return yaml.safe_load(spec_file)


def _load_oauth_spec():
    return _load_spec()["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]


def _without(config, key):
    return {name: value for name, value in config.items() if name != key}


@pytest.mark.parametrize(
    "config, is_valid",
    [
        pytest.param(_CLIENT_CREDENTIALS, True, id="legacy_config_without_auth_type"),
        pytest.param({**_CLIENT_CREDENTIALS, "auth_type": "Client"}, True, id="explicit_client_auth_type"),
        pytest.param(_JWT_CREDENTIALS, True, id="jwt_config"),
        pytest.param(_without(_JWT_CREDENTIALS, "private_key"), False, id="jwt_without_private_key"),
        pytest.param(_without(_JWT_CREDENTIALS, "username"), False, id="jwt_without_username"),
        pytest.param(_without(_CLIENT_CREDENTIALS, "refresh_token"), False, id="client_without_refresh_token"),
        pytest.param({"client_id": "a_client_id"}, False, id="client_id_only"),
        pytest.param({**_CLIENT_CREDENTIALS, "auth_type": "Bogus"}, False, id="unknown_auth_type"),
    ],
)
def test_conditional_required_fields_per_auth_type(config, is_valid):
    """Neither credential set can be required at the top level once both auth types exist, so they are
    required conditionally through allOf/if-then. auth_type alone selects the set, and a config saved
    before the JWT option existed has no auth_type at all."""
    errors = list(Draft7Validator(_load_spec()["connectionSpecification"]).iter_errors(config))

    assert bool(not errors) is is_valid, [error.message for error in errors]


def test_auth_type_stays_in_the_expanded_part_of_the_form():
    """auth_type is the OAuth predicate field, so the "Authenticate" button renders beside it. It used
    to be a hidden const, which the webapp treats as required and keeps expanded; as a plain optional
    enum it would sort into the collapsed "Optional fields" section and take the button with it."""
    auth_type = _load_spec()["connectionSpecification"]["properties"]["auth_type"]

    assert auth_type["always_show"] is True
    assert auth_type["default"] == "Client"
    assert "auth_type" not in _load_spec()["connectionSpecification"]["required"], "legacy configs have no auth_type"


def test_oauth_spec_includes_pkce_parameters():
    oauth_spec = _load_oauth_spec()
    consent_url = oauth_spec["consent_url"]

    assert "code_challenge=" in consent_url
    assert "code_challenge_method=S256" in consent_url
    assert oauth_spec["access_token_params"]["code_verifier"] == "{{ state_value }}"
    assert oauth_spec["state"] == {"min": 43, "max": 128}
    assert "replace('+', '-')" in consent_url
    assert "replace('/', '_')" in consent_url
    assert "replace('=', '')" in consent_url


def test_consent_url_renders_unpadded_base64url_code_challenge():
    oauth_spec = _load_oauth_spec()
    verifier = "v" * 43
    environment = jinja2.Environment()

    # This stub mirrors the platform filter's padded output; the real filter lives in airbyte-platform.
    environment.filters["codechallengeS256"] = lambda value: base64.b64encode(hashlib.sha256(value.encode()).digest()).decode()
    rendered_url = environment.from_string(oauth_spec["consent_url"]).render(
        is_sandbox=False,
        client_id_param="client_id=dummy-client",
        redirect_uri_param="redirect_uri=https%3A%2F%2Fexample.com%2Fcallback",
        scopes_param="scope=api",
        state_param="state=dummy-state",
        state_value=verifier,
    )

    query = parse_qs(urlparse(rendered_url).query)
    code_challenge = query["code_challenge"][0]
    expected_code_challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()

    assert len(code_challenge) == 43
    assert not any(character in code_challenge for character in "+/=")
    assert code_challenge == expected_code_challenge
    assert query["code_challenge_method"][0] == "S256"
