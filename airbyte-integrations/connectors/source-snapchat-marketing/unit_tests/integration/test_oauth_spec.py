#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
import yaml


_MANIFEST_PATH = Path(__file__).resolve().parents[2] / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    with open(_MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def oauth_spec(manifest):
    return manifest["spec"]["advanced_auth"]["oauth_config_specification"]


SERVER_MANAGED_FIELDS = {"client_id", "client_secret"}


def test_oauth_user_input_does_not_contain_server_managed_fields(oauth_spec):
    """Regression: client_id/client_secret must NOT appear in
    oauth_user_input_from_connector_config_specification.

    These are server-managed OAuth credentials. Listing them as user inputs
    causes the platform to overwrite real credentials with masked values
    ('**********') during re-authentication, breaking the consent URL.

    See: https://github.com/airbytehq/oncall/issues/12909
    """
    user_input_props = oauth_spec["oauth_user_input_from_connector_config_specification"].get("properties", {})
    found = SERVER_MANAGED_FIELDS & set(user_input_props.keys())
    assert not found, (
        f"Server-managed OAuth fields {found} must not be in "
        f"oauth_user_input_from_connector_config_specification — "
        f"they cause masked values to overwrite real credentials on re-auth"
    )


def test_server_managed_fields_in_server_input_spec(oauth_spec):
    """Verify client_id/client_secret remain in complete_oauth_server_input_specification."""
    server_input_props = oauth_spec["complete_oauth_server_input_specification"]["properties"]
    for field in SERVER_MANAGED_FIELDS:
        assert field in server_input_props, f"{field} must be in complete_oauth_server_input_specification"


def test_server_managed_fields_in_server_output_spec(oauth_spec):
    """Verify client_id/client_secret remain in complete_oauth_server_output_specification."""
    server_output_props = oauth_spec["complete_oauth_server_output_specification"]["properties"]
    for field in SERVER_MANAGED_FIELDS:
        assert field in server_output_props, f"{field} must be in complete_oauth_server_output_specification"


def test_refresh_token_in_oauth_output_spec(oauth_spec):
    """Verify refresh_token is in complete_oauth_output_specification."""
    output_props = oauth_spec["complete_oauth_output_specification"]["properties"]
    assert "refresh_token" in output_props
