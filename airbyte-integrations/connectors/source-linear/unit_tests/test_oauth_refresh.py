# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

from airbyte_cdk.models import FailureType, SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
CONFIG = {
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


def test_oauth_refresh_persists_rotated_token_and_uses_new_access_token():
    config = deepcopy(CONFIG)
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)
    graphql_requests = []

    def token_request(*, method, url, **kwargs):
        assert method == "POST"
        assert url == TOKEN_URL
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
        graphql_requests.append(request)
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
    assert updated_config["credentials"]["refresh_token"] == "new-refresh-token"
    assert updated_config["credentials"]["access_token"] == "new-access-token"
    assert "token_expiry_date" in updated_config["credentials"]
    assert graphql_requests[0].headers["Authorization"] == "Bearer new-access-token"


def test_invalid_refresh_token_is_reported_as_configuration_error():
    config = deepcopy(CONFIG)
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)
    stream = next(stream for stream in source.streams(config=config) if stream.name == "issues")
    retriever = stream._stream_partition_generator._partition_factory._retriever
    authenticator = retriever.requester.authenticator

    def token_request(*, method, url, **kwargs):
        return _response(
            TOKEN_URL,
            400,
            {
                "error": "invalid_request",
                "error_description": "Refresh token revoked",
            },
        )

    with patch("requests.request", side_effect=token_request):
        with pytest.raises(AirbyteTracedException) as error:
            authenticator.get_access_token()

    assert error.value.failure_type == FailureType.config_error
    assert "Refresh token is invalid or expired" in str(error.value)
    assert not isinstance(error.value.__cause__, requests.exceptions.HTTPError)
