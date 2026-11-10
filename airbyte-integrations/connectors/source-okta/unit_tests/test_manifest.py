# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import json
from urllib.parse import parse_qs

import jwt
import pytest
from conftest import get_source
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://example.okta.com"
TOKEN_URL = f"{BASE}/oauth2/v1/token"
START = "2024-01-01T00:00:00Z"


def config(credentials: dict | None = None) -> dict:
    return {"domain": "example", "start_date": START, "credentials": credentials or {"auth_type": "api_token", "api_token": "test-token"}}


def read_stream(settings: dict, stream: str = "custom_roles", state: list | None = None):
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental if stream in ("users", "logs") else SyncMode.full_refresh).build()
    return read(get_source(settings, state), config=settings, catalog=catalog, state=state)


def page(http: HttpMocker, authorization: str, second: bool = False) -> HttpRequest:
    url = f"{BASE}/api/v1/iam/roles"
    request = HttpRequest(
        url, query_params={"after": "next", "limit": "200"} if second else {"limit": "200"}, headers={"Authorization": authorization}
    )
    links = f'<{url}?after=next&limit=200>; rel="next"'
    if second:
        links += f', <{url}?after=next&limit=200>; rel="self"'
    http.get(request, HttpResponse(json.dumps({"roles": [{"id": "second" if second else "first"}]}), 200, headers={"Link": links}))
    return request


@pytest.mark.parametrize("empty", [False, True])
def test_api_token(empty: bool) -> None:
    with HttpMocker() as http:
        request = HttpRequest(f"{BASE}/api/v1/iam/roles", query_params={"limit": "200"}, headers={"Authorization": "SSWS test-token"})
        http.get(request, HttpResponse(json.dumps({"roles": [] if empty else [{"id": "one"}]}), 200))
        output = read_stream(config())
        assert [m.record.data["id"] for m in output.records] == ([] if empty else ["one"])
        http.assert_number_of_calls(request, 1)
        assert not output.errors


def test_oauth_refresh() -> None:
    settings = config({"auth_type": "oauth2.0", "client_id": "client", "client_secret": "secret", "refresh_token": "refresh"})
    with HttpMocker() as http:
        token_request = HttpRequest(
            TOKEN_URL,
            headers={"Authorization": "Basic " + base64.b64encode(b"client:secret").decode()},
            body="grant_type=refresh_token&refresh_token=refresh",
        )
        http.post(token_request, HttpResponse(json.dumps({"access_token": "access", "expires_in": 3600}), 200))
        first = page(http, "Bearer access")
        second = page(http, "Bearer access", second=True)
        output = read_stream(settings)
        assert [m.record.data["id"] for m in output.records] == ["first", "second"]
        for request in (token_request, first, second):
            http.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("escaped", [False, True])
def test_private_key(escaped: bool) -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    settings = config(
        {
            "auth_type": "oauth2.0_private_key",
            "client_id": "client",
            "key_id": "key-id",
            "scope": "okta.users.read",
            "private_key": pem.replace("\n", "\\n") if escaped else pem,
        }
    )
    with HttpMocker() as http:
        token_requests = []

        def token_response(request, context) -> dict:
            token_requests.append(parse_qs(request.text))
            return {"access_token": "access", "expires_in": 3600}

        http._mocker.post(TOKEN_URL, json=token_response)
        first = page(http, "Bearer access")
        second = page(http, "Bearer access", second=True)
        output = read_stream(settings)
        assert [m.record.data["id"] for m in output.records] == ["first", "second"]
        assert len(token_requests) == 1
        form = token_requests[0]
        assertion = form.pop("client_assertion")[0]
        assert form == {
            "grant_type": ["client_credentials"],
            "client_id": ["client"],
            "scope": ["okta.users.read"],
            "client_assertion_type": ["urn:ietf:params:oauth:client-assertion-type:jwt-bearer"],
        }
        claims = jwt.decode(assertion, key.public_key(), algorithms=["RS256"], audience=TOKEN_URL)
        assert claims["iss"] == claims["sub"] == "client"
        assert claims["aud"] == TOKEN_URL
        assert claims["exp"] - claims["iat"] == 300
        assert claims["jti"]
        assert jwt.get_unverified_header(assertion)["kid"] == "key-id"
        for request in (first, second):
            http.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("domain", ["example", "12345"])
def test_legacy_config(domain: str, capsys: pytest.CaptureFixture) -> None:
    settings = {"base_url": f"https://{domain}.okta.com", "token": "legacy", "start_date": START}
    with HttpMocker() as http:
        request = HttpRequest(
            f"https://{domain}.okta.com/api/v1/iam/roles", query_params={"limit": "200"}, headers={"Authorization": "SSWS legacy"}
        )
        http.get(request, HttpResponse('{"roles": [{"id": "legacy-record"}]}', 200))
        output = read_stream(settings)
        assert [m.record.data["id"] for m in output.records] == ["legacy-record"]
        controls = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith('{"type":"CONTROL"')]
        assert controls
        migrated = controls[-1]["control"]["connectorConfig"]["config"]
        assert migrated["domain"] == domain
        assert migrated["credentials"] == {"auth_type": "api_token", "api_token": "legacy"}


@pytest.mark.parametrize("stream,cursor", [("users", "lastUpdated"), ("logs", "published")])
@pytest.mark.parametrize("with_state", [False, True])
def test_incremental(stream: str, cursor: str, with_state: bool) -> None:
    bookmark = "2024-02-01T00:00:00.000Z" if stream == "users" else "2024-02-01T00:00:00Z"
    state = StateBuilder().with_stream_state(stream, {cursor: bookmark}).build() if with_state else []
    since = bookmark if with_state else START
    params = {"limit": "200"}
    if stream == "logs":
        params["since"] = since
    else:
        statuses = " or ".join(
            f'status eq "{status}"'
            for status in ["ACTIVE", "DEPROVISIONED", "LOCKED_OUT", "PASSWORD_EXPIRED", "PROVISIONED", "RECOVERY", "STAGED", "SUSPENDED"]
        )
        params["filter"] = f'lastUpdated gt "{since[:19]}.000Z" and ({statuses})'
    record = {"id": "one", "uuid": "one", cursor: "2024-03-01T00:00:00.123Z"}
    with HttpMocker() as http:
        request = HttpRequest(f"{BASE}/api/v1/{stream}", query_params=params, headers={"Authorization": "SSWS test-token"})
        http.get(request, HttpResponse(json.dumps([record]), 200))
        output = read_stream(config(), stream, state)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "one"
        expected = "2024-03-01T00:00:00Z" if stream == "logs" else record[cursor]
        assert output.records[0].record.data[cursor] == expected
        expected_state = expected if stream == "logs" else "2024-03-01T00:00:00.123000Z"
        assert output.most_recent_state.stream_state.__dict__[cursor] == expected_state
        http.assert_number_of_calls(request, 1)


def test_logs_invalid_since_is_ignored() -> None:
    with HttpMocker() as http:
        request = HttpRequest(f"{BASE}/api/v1/logs", query_params=ANY_QUERY_PARAMS, headers={"Authorization": "SSWS test-token"})
        http.get(request, HttpResponse('{"errorCode":"E0000001","errorSummary":"Invalid since parameter"}', 400))
        output = read_stream(config(), "logs")
        assert output.records == []
        assert not output.errors
        assert not any(log.log.level == "ERROR" for log in output.logs)
        assert any("Invalid since parameter" in log.log.message for log in output.logs)


@pytest.mark.parametrize("error", ["invalid_grant", "invalid_client"])
def test_oauth_rejection_is_config_error(error: str) -> None:
    settings = config({"auth_type": "oauth2.0", "client_id": "client", "client_secret": "secret", "refresh_token": "refresh"})
    with HttpMocker() as http:
        token_request = HttpRequest(TOKEN_URL, body="grant_type=refresh_token&refresh_token=refresh")
        http.post(token_request, HttpResponse(json.dumps({"error": error}), 400))
        catalog = CatalogBuilder().with_stream("custom_roles", SyncMode.full_refresh).build()
        output = read(get_source(settings), config=settings, catalog=catalog, expecting_exception=True)
        assert output.records == []
        assert any(message.trace.error.failure_type.value == "config_error" for message in output.errors)
        http.assert_number_of_calls(token_request, 1)
