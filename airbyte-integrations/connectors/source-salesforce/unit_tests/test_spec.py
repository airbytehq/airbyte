#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import base64
import hashlib
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import jinja2
import jsonschema
import pytest
import yaml
from source_salesforce import SourceSalesforce


SPEC_PATH = Path(__file__).resolve().parents[1] / "source_salesforce" / "spec.yaml"


def _load_spec():
    with SPEC_PATH.open() as spec_file:
        return yaml.safe_load(spec_file)


def _load_connection_spec():
    return _load_spec()["connectionSpecification"]


def _load_oauth_spec():
    return _load_spec()["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]


def test_auth_type_default_and_enum_order():
    connection_spec = _load_connection_spec()
    auth_type = connection_spec["properties"]["auth_type"]

    assert auth_type["enum"] == ["ClientCredentials", "Client"]
    assert auth_type["default"] == "ClientCredentials"
    assert auth_type["always_show"] is True
    assert auth_type["order"] == 0
    assert connection_spec["required"] == ["client_id", "client_secret"]


def test_secret_fields_are_marked_in_top_level_properties():
    properties = _load_connection_spec()["properties"]

    assert properties["client_secret"]["airbyte_secret"] is True
    assert properties["refresh_token"]["airbyte_secret"] is True


def test_oauth_config_paths_are_flat_and_present_in_connection_spec():
    spec = _load_spec()
    properties = spec["connectionSpecification"]["properties"]
    oauth_config = spec["advanced_auth"]["oauth_config_specification"]

    for output_name in (
        "complete_oauth_output_specification",
        "complete_oauth_server_output_specification",
        "oauth_user_input_from_connector_config_specification",
    ):
        for property_spec in oauth_config[output_name]["properties"].values():
            if "path_in_connector_config" not in property_spec:
                continue

            path = property_spec["path_in_connector_config"]
            assert len(path) == 1
            assert path[0] in properties


@pytest.mark.parametrize(
    ("connection_config", "is_valid"),
    [
        (
            {
                "auth_type": "ClientCredentials",
                "domain_url": "https://acme.my.salesforce.com",
                "client_id": "consumer-key",
                "client_secret": "consumer-secret",
            },
            True,
        ),
        (
            {
                "auth_type": "Client",
                "client_id": "consumer-key",
                "client_secret": "consumer-secret",
                "refresh_token": "refresh-token",
            },
            True,
        ),
        (
            {
                "client_id": "consumer-key",
                "client_secret": "consumer-secret",
                "refresh_token": "refresh-token",
            },
            True,
        ),
        (
            {
                "auth_type": "ClientCredentials",
                "domain_url": "https://login.salesforce.com",
                "client_id": "consumer-key",
                "client_secret": "consumer-secret",
            },
            False,
        ),
    ],
    ids=[
        "client-credentials",
        "client",
        "client-without-auth-type",
        "client-credentials-login-domain",
    ],
)
def test_connection_spec_validates_authentication_methods(connection_config, is_valid):
    validator = jsonschema.Draft7Validator(_load_connection_spec())

    assert validator.is_valid(connection_config) == is_valid


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


def test_spec_declares_groups_and_sections():
    """The stepped setup form: two sections, "Connect account" (checked) and "Review & set up" (covered by the full check)."""
    schema = _load_connection_spec()

    assert [group["id"] for group in schema["groups"]] == ["account", "filters", "advanced"]
    assert schema["sections"] == [
        {
            "id": "account",
            "title": "Connect account",
            "order": 0,
            "description": "Choose the environment and sign in to Salesforce.",
            "groups": ["account", "filters"],
            "check": True,
        },
        {
            "id": "review",
            "title": "Review & set up",
            "order": 1,
            "description": "Name your source and check the optional settings.",
            "groups": ["advanced"],
        },
    ]
    # Every section group is declared, and every visible property belongs to a group of some section.
    declared_groups = {group["id"] for group in schema["groups"]}
    section_groups = {group for section in schema["sections"] for group in section["groups"]}
    assert section_groups <= declared_groups
    grouped = {name: prop["group"] for name, prop in schema["properties"].items() if "group" in prop}
    assert grouped == {
        "auth_type": "account",
        "domain_url": "account",
        "is_sandbox": "account",
        "client_id": "account",
        "client_secret": "account",
        "refresh_token": "account",
        "start_date": "filters",
        "end_date": "filters",
        "streams_criteria": "filters",
        "preserve_na_values": "filters",
        "force_use_bulk_api": "advanced",
        "stream_slice_step": "advanced",
        "lookback_window": "advanced",
    }
    assert set(grouped.values()) <= section_groups
    # Every property, the authentication method selector included, belongs to a group.
    assert set(grouped) == set(schema["properties"])
    # The required fields all belong to the first section, so its check can validate them.
    assert {grouped[name] for name in schema["required"]} == {"account"}


def test_spec_orders_properties_as_the_form_shows_them():
    """The form shows the groups in their declared order and, within a group, the properties by `order`."""
    properties = _load_connection_spec()["properties"]

    orders = {name: prop["order"] for name, prop in properties.items() if "order" in prop}
    assert len(set(orders.values())) == len(orders)
    by_group = {}
    for name in sorted(orders, key=orders.get):
        by_group.setdefault(properties[name]["group"], []).append(name)
    assert by_group == {
        "account": ["auth_type", "domain_url", "is_sandbox", "client_id", "client_secret", "refresh_token"],
        "filters": ["start_date", "end_date", "streams_criteria", "preserve_na_values"],
        "advanced": ["force_use_bulk_api", "stream_slice_step", "lookback_window"],
    }


def test_source_spec_carries_the_sections():
    """The CDK serves spec.yaml as is, so the sections reach the platform."""
    schema = SourceSalesforce(None, None, None).spec(None).connectionSpecification

    assert [section["id"] for section in schema["sections"]] == ["account", "review"]
    assert [section.get("check") for section in schema["sections"]] == [True, None]
