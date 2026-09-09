# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import requests

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
OAUTH_CONFIG = {
    "credentials": {
        "auth_type": "OAuth2.0",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "refresh_token": "old-refresh-token",
    },
    "start_date": "2024-01-01T00:00:00.000Z",
}
TOKEN_URL = "https://api.linear.app/oauth/token"
GRAPHQL_URL = "https://api.linear.app/graphql"


def _response(url: str, status_code: int, payload: dict, request=None) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.url = url
    response.request = request
    response.headers = {}
    response._content = json.dumps(payload).encode()
    return response


def test_oauth_only_config_gains_no_api_key_after_normalization():
    config = deepcopy(OAUTH_CONFIG)
    src = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)

    assert "api_key" not in src._config["credentials"]
    assert "api_key" not in src._config
    assert src._config["credentials"]["auth_type"] == "OAuth2.0"


def test_oauth_refresh_control_message_contains_no_api_key():
    config = deepcopy(OAUTH_CONFIG)
    config["credentials"]["token_expiry_date"] = "2000-01-01T00:00:00.000Z"
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)

    def token_request(*, method, url, **kwargs):
        return _response(
            TOKEN_URL,
            200,
            {
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "expires_in": 3600,
            },
        )

    def graphql_request(request, **kwargs):
        return _response(
            GRAPHQL_URL,
            200,
            {"data": {"issues": {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}}},
            request,
        )

    catalog = CatalogBuilder().with_stream("issues", SyncMode.full_refresh).build()
    with patch("requests.request", side_effect=token_request), patch("requests.sessions.Session.send", side_effect=graphql_request):
        output = read(source, config, catalog)

    assert not output.errors
    control_messages = output.get_message_by_types([Type.CONTROL])
    assert len(control_messages) == 1
    updated_config = control_messages[0].control.connectorConfig.config
    assert updated_config["credentials"]["access_token"] == "new-access-token"
    assert updated_config["credentials"]["refresh_token"] == "new-refresh-token"
    assert "token_expiry_date" in updated_config["credentials"]
    assert "api_key" not in updated_config["credentials"]
    assert "api_key" not in updated_config


def test_flat_api_key_config_migrates_to_nested_credentials():
    config = {"api_key": "test-api-key"}
    src = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)

    assert src._config["credentials"] == {"auth_type": "API Key", "api_key": "test-api-key"}


def test_half_migrated_api_key_config_gets_nested_api_key():
    config = {"api_key": "test-api-key", "credentials": {"auth_type": "API Key"}}
    src = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)

    assert src._config["credentials"] == {"auth_type": "API Key", "api_key": "test-api-key"}


def test_empty_flat_api_key_is_not_migrated():
    config = {
        "api_key": "",
        "credentials": {
            "auth_type": "OAuth2.0",
            "client_id": "c",
            "client_secret": "s",
            "refresh_token": "r",
        },
    }
    src = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)

    assert "api_key" not in src._config["credentials"]
