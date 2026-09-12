#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Tests for the ``advanced_auth`` (declarative OAuth) block in ``spec.json``.

The platform's DeclarativeOAuthFlow builds the consent and token URLs from the
spec, substituting ``dc_region`` from the user's config. These tests pin the
contract: every data center selectable in the connection spec must resolve to a
Zoho accounts domain in both OAuth URLs, and every OAuth output path must point
at a real connection-spec property.
"""

import json
import re
from pathlib import Path

import pytest


SPEC = json.loads((Path(__file__).parent.parent / "source_zoho_crm" / "spec.json").read_text())
CONNECTION_PROPERTIES = SPEC["connectionSpecification"]["properties"]
OAUTH_SPEC = SPEC["advanced_auth"]["oauth_config_specification"]
CONNECTOR_INPUT = OAUTH_SPEC["oauth_connector_input_specification"]

# Domains documented at https://www.zoho.com/crm/developer/docs/api/v2/multi-dc.html
DC_REGION_TO_ACCOUNTS_DOMAIN = {
    "US": "com",
    "AU": "com.au",
    "EU": "eu",
    "IN": "in",
    "CN": "com.cn",
    "JP": "jp",
}


def test_auth_flow_type_is_oauth2():
    assert SPEC["advanced_auth"]["auth_flow_type"] == "oauth2.0"


@pytest.mark.parametrize("url_key", ["consent_url", "access_token_url"])
def test_oauth_urls_map_every_dc_region(url_key):
    """The inline Jinja mapping in each OAuth URL must cover every ``dc_region`` enum value."""
    template = CONNECTOR_INPUT[url_key]
    mapping_literal = re.search(r"\{\{\s*(\{[^}]*\})\[dc_region\]\s*\}\}", template)
    assert mapping_literal, f"{url_key} must map dc_region to a Zoho accounts domain"
    mapping = json.loads(mapping_literal.group(1).replace("'", '"'))

    dc_region_enum = set(CONNECTION_PROPERTIES["dc_region"]["enum"])
    assert set(mapping) == dc_region_enum, f"{url_key} mapping must cover exactly the dc_region enum values"
    assert mapping == DC_REGION_TO_ACCOUNTS_DOMAIN


def test_consent_url_requests_offline_access():
    """Zoho only returns a refresh token when offline access and consent are requested."""
    consent_url = CONNECTOR_INPUT["consent_url"]
    assert "access_type=offline" in consent_url
    assert "prompt=consent" in consent_url


def test_scopes_cover_connector_endpoints_and_join_with_comma():
    """The connector reads settings (modules/fields) and module records; Zoho separates scopes with commas."""
    scopes = {entry["scope"] for entry in CONNECTOR_INPUT["scopes"]}
    assert scopes == {"ZohoCRM.settings.READ", "ZohoCRM.modules.READ"}
    assert CONNECTOR_INPUT["scopes_join_strategy"] == "comma"


def test_oauth_paths_exist_in_connection_spec():
    """Every path_in_connector_config must target a property the connection spec declares."""
    sections = [
        OAUTH_SPEC["oauth_user_input_from_connector_config_specification"],
        OAUTH_SPEC["complete_oauth_output_specification"],
        OAUTH_SPEC["complete_oauth_server_output_specification"],
    ]
    for section in sections:
        for name, prop in section["properties"].items():
            path = prop["path_in_connector_config"]
            assert path == [name], f"{name} must map to the top-level spec property of the same name"
            assert name in CONNECTION_PROPERTIES, f"{name} is not a connection spec property"


def test_extract_output_is_refresh_token_only():
    """Zoho's token response is exchanged for a long-lived refresh token; nothing else persists."""
    assert CONNECTOR_INPUT["extract_output"] == ["refresh_token"]
