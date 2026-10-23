#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import base64
import hashlib
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import jinja2
import pytest
import yaml


SPEC_PATH = Path(__file__).resolve().parents[1] / "source_salesforce" / "spec.yaml"


def _load_oauth_spec():
    with SPEC_PATH.open() as spec_file:
        spec = yaml.safe_load(spec_file)
    oauth_spec = spec["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]
    return oauth_spec


def test_auth_type_spec_exposes_both_authentication_methods():
    with SPEC_PATH.open() as spec_file:
        spec = yaml.safe_load(spec_file)

    auth_type = spec["connectionSpecification"]["properties"]["auth_type"]
    assert auth_type["enum"] == ["Client", "ClientCredentials"]
    assert auth_type["default"] == "Client"
    assert auth_type["always_show"] is True
    assert auth_type["order"] == 0
    assert spec["connectionSpecification"]["required"] == ["client_id", "client_secret"]


@pytest.mark.parametrize(
    "domain_url",
    [
        "https://acme.my.salesforce.com",
        "https://acme.my.salesforce.com/",
        "https://acme--uat.sandbox.my.salesforce.com",
        "https://acme-dev-ed.develop.my.salesforce.com",
        "https://x.scratch.my.salesforce.com",
        "https://x.trailblaze.my.salesforce.com",
        "",
    ],
)
def test_domain_url_pattern_accepts_salesforce_my_domain_urls(domain_url):
    with SPEC_PATH.open() as spec_file:
        spec = yaml.safe_load(spec_file)

    pattern = spec["connectionSpecification"]["properties"]["domain_url"]["pattern"]
    assert re.fullmatch(pattern, domain_url)


@pytest.mark.parametrize(
    "domain_url",
    [
        "https://login.salesforce.com",
        "https://test.salesforce.com",
        "https://acme.lightning.force.com",
        "http://acme.my.salesforce.com",
        "https://acme.my.salesforce.com/services",
    ],
)
def test_domain_url_pattern_rejects_non_my_domain_urls(domain_url):
    with SPEC_PATH.open() as spec_file:
        spec = yaml.safe_load(spec_file)

    pattern = spec["connectionSpecification"]["properties"]["domain_url"]["pattern"]
    assert re.fullmatch(pattern, domain_url) is None


def test_advanced_auth_is_still_scoped_to_client():
    with SPEC_PATH.open() as spec_file:
        spec = yaml.safe_load(spec_file)

    assert spec["advanced_auth"]["predicate_key"] == ["auth_type"]
    assert spec["advanced_auth"]["predicate_value"] == "Client"


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
