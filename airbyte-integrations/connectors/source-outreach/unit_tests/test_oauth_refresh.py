# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs

import requests

from airbyte_cdk.models import FailureType, SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
CONFIG = {
    "client_id": "client-id",
    "client_secret": "client-secret",
    "refresh_token": "old-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2024-01-01T00:00:00Z",
}
TOKEN_URL = "https://api.outreach.io/oauth/token"
API_URL = "https://api.outreach.io/api/v2/"
CATALOG = CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build()


def _response(url: str, status_code: int, payload: dict, request=None) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.url = url
    response.request = request
    response.headers = {}
    response._content = json.dumps(payload).encode()
    return response


def _token_request_body(kwargs: dict) -> dict:
    body = kwargs.get("data") or kwargs.get("json") or {}
    if isinstance(body, (str, bytes)):
        return {key: values[-1] for key, values in parse_qs(body).items()}
    return body


def _mailing(mailing_id: int) -> dict:
    return {
        "id": mailing_id,
        "attributes": {"updatedAt": "2024-02-01T00:00:00.000Z"},
        "relationships": {},
    }


def _records(output) -> list[dict]:
    return [message.record.data for message in output.get_message_by_types([Type.RECORD])]


def _control_messages(captured_stdout: str) -> list[dict]:
    messages = []
    for line in captured_stdout.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("type") == "CONTROL":
            messages.append(message)
    return messages


def test_refresh_persists_rotated_refresh_token(capsys):
    config = deepcopy(CONFIG)
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)
    token_requests = []
    api_requests = []

    def token_request(*, method, url, **kwargs):
        token_requests.append((method, url, kwargs))
        return _response(
            TOKEN_URL,
            200,
            {
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "expires_in": 7200,
                "token_type": "bearer",
            },
        )

    def api_request(request, **kwargs):
        api_requests.append(request)
        return _response(API_URL + "mailings", 200, {"data": [_mailing(1)], "links": {}}, request)

    with patch("requests.request", side_effect=token_request), patch("requests.sessions.Session.send", side_effect=api_request):
        output = read(source, config, CATALOG)

    assert not output.errors
    assert len(token_requests) == 1
    control_messages = _control_messages(capsys.readouterr().out)
    assert len(control_messages) == 1
    updated_config = control_messages[0]["control"]["connectorConfig"]["config"]
    assert updated_config["refresh_token"] == "new-refresh-token"
    assert updated_config["access_token"] == "new-access-token"
    assert "token_expiry_date" in updated_config
    assert api_requests[0].headers["Authorization"] == "Bearer new-access-token"
    assert token_requests[0][0] == "POST"
    assert token_requests[0][1] == TOKEN_URL
    assert _token_request_body(token_requests[0][2])["refresh_token"] == "old-refresh-token"


def test_expired_access_token_401_mid_sync_refreshes_and_retries(capsys):
    config = deepcopy(CONFIG)
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)
    token_requests = []
    api_requests = []
    page_two_attempts = 0

    def token_request(*, method, url, **kwargs):
        token_requests.append((method, url, kwargs))
        token_number = len(token_requests)
        return _response(
            TOKEN_URL,
            200,
            {
                "access_token": f"token-{token_number}",
                "refresh_token": f"refresh-{token_number}",
                "expires_in": 7200,
                "token_type": "bearer",
            },
        )

    def api_request(request, **kwargs):
        nonlocal page_two_attempts
        api_requests.append(request)
        if "page=2" in request.url:
            page_two_attempts += 1
            if page_two_attempts == 1:
                return _response(
                    request.url,
                    401,
                    {
                        "id": "expiredAccessToken",
                        "title": "Expired Access Token",
                        "detail": "Please get a new access token and try again.",
                    },
                    request,
                )
            return _response(request.url, 200, {"data": [_mailing(2)], "links": {}}, request)
        return _response(
            request.url,
            200,
            {
                "data": [_mailing(1)],
                "links": {"next": API_URL + "mailings?page=2"},
            },
            request,
        )

    with (
        patch("requests.request", side_effect=token_request),
        patch("requests.sessions.Session.send", side_effect=api_request),
        patch("time.sleep"),
    ):
        output = read(source, config, CATALOG)

    assert not output.errors
    assert [record["id"] for record in _records(output)] == [1, 2]
    assert len(token_requests) == 2
    assert _token_request_body(token_requests[1][2])["refresh_token"] == "refresh-1"
    page_two_requests = [request for request in api_requests if "page=2" in request.url]
    assert page_two_requests[-1].headers["Authorization"] == "Bearer token-2"
    control_messages = _control_messages(capsys.readouterr().out)
    assert control_messages[-1]["control"]["connectorConfig"]["config"]["refresh_token"] == "refresh-2"


def test_access_token_reused_until_expiry():
    config = deepcopy(CONFIG)
    config["access_token"] = "existing"
    config["token_expiry_date"] = "2099-01-01T00:00:00.000Z"
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)
    api_requests = []

    def token_request(*args, **kwargs):
        raise AssertionError("The token endpoint should not be called before expiry")

    def api_request(request, **kwargs):
        api_requests.append(request)
        return _response(request.url, 200, {"data": [_mailing(1)], "links": {}}, request)

    with patch("requests.request", side_effect=token_request), patch("requests.sessions.Session.send", side_effect=api_request):
        output = read(source, config, CATALOG)

    assert not output.errors
    assert api_requests[0].headers["Authorization"] == "Bearer existing"


def test_invalid_refresh_token_is_config_error():
    config = deepcopy(CONFIG)
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config)

    def token_request(*, method, url, **kwargs):
        return _response(
            TOKEN_URL,
            400,
            {"error": "invalid_grant", "error_description": "Refresh token is invalid"},
        )

    with patch("requests.request", side_effect=token_request):
        output = read(source, config, CATALOG)

    assert output.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
