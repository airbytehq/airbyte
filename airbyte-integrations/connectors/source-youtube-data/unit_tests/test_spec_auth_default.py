# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
OAUTH_CONFIG: Mapping[str, Any] = {
    "credentials": {
        "auth_method": "oauth2.0",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
    },
    "channel_ids": ["UC..."],
}


def test_oauth_is_first_spec_authentication_method() -> None:
    """The UI seeds a new source form from the first oneOf branch, so ordering decides the default."""
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=OAUTH_CONFIG)
    specification = source.spec(logging.getLogger(__name__))
    branches = specification.connectionSpecification["properties"]["credentials"]["oneOf"]

    first_branch = branches[0]
    assert first_branch["title"] == "Google OAuth 2.0"
    assert first_branch["properties"]["auth_method"]["const"] == "oauth2.0"
    assert any(branch["properties"]["auth_method"]["const"] == "api_key" for branch in branches)


def test_authentication_method_selection_uses_stored_config() -> None:
    api_key_config = {
        "credentials": {"auth_method": "api_key", "api_key": "test-api-key"},
        "channel_ids": ["UC..."],
    }
    oauth_config = {
        **OAUTH_CONFIG,
        "credentials": {**OAUTH_CONFIG["credentials"]},
    }

    for config, expected_authenticator in (
        (api_key_config, ApiKeyAuthenticator),
        (oauth_config, DeclarativeOauth2Authenticator),
    ):
        source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=config)
        channels_stream = next(stream for stream in source.streams(config=config) if stream.name == "channels")
        authenticator = next(iter(channels_stream.generate_partitions()))._retriever.requester.authenticator

        assert type(authenticator) is expected_authenticator
