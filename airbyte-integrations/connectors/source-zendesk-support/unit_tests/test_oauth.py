# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    OAuthAuthenticator as OAuthAuthenticatorModel,
)
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _load_manifest() -> dict:
    return yaml.safe_load(_MANIFEST_PATH.read_text())


def _build_oauth_authenticator(token_expiry_date: str):
    manifest = _load_manifest()
    auth_def = manifest["definitions"]["oauth_refresh_authenticator"]
    config = {
        "subdomain": "test",
        "credentials": {
            "credentials": "oauth2_refresh",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "token_expiry_date": token_expiry_date,
        },
    }
    return ModelToComponentFactory().create_component(OAuthAuthenticatorModel, auth_def, config)


def test_oauth_input_specification_extracts_expires_in():
    """The OAuth completion flow must extract `expires_in` so the platform persists a `token_expiry_date`.

    Without it, the config never stores an expiry, the CDK treats the token as already expired, and
    the connector refreshes on the very first `check` — rotating Zendesk's single-use refresh token
    and bricking the connection (oncall #13130).
    """
    manifest = _load_manifest()
    extract_output = manifest["spec"]["advanced_auth"]["oauth_config_specification"][
        "oauth_connector_input_specification"
    ]["extract_output"]
    assert "expires_in" in extract_output


@pytest.mark.parametrize(
    "token_expiry_date, expected_expired",
    [
        pytest.param("2999-01-01T00:00:00Z", False, id="valid_future_expiry_does_not_refresh"),
        pytest.param("", True, id="missing_expiry_forces_refresh"),
    ],
)
def test_token_expiry_controls_refresh(token_expiry_date, expected_expired):
    """A persisted future `token_expiry_date` prevents a premature refresh (and thus token rotation).

    When the expiry is missing (empty), the authenticator considers the token expired and refreshes
    immediately, which is what consumes Zendesk's single-use refresh token on the first `check`.
    """
    authenticator = _build_oauth_authenticator(token_expiry_date)
    assert authenticator.token_has_expired() is expected_expired
