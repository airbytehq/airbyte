# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server coverage for the OAuth 2.0 branch's token lifecycle.

These tests start from the config shape the platform persists after consent or after a refresh
CONTROL: `credentials.access_token` plus `credentials.token_expiry_date` (Java `Instant.toString()`),
not the cold config the other OAuth tests use. They lock in that a valid stored token is reused,
an expired one is refreshed exactly once with the expiry written back, a rejected refresh fails as
`config_error`, a stream 401 refresh persists a rotated refresh token, and streams share one refresh.
"""

import json
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import UptickRequestBuilder


_STREAM = "servicegroups"
_TOKEN_URL = UptickRequestBuilder.token_endpoint()
_STORED_ACCESS_TOKEN = "stored-access-token"
_FUTURE_EXPIRY = "2099-01-01T00:00:00Z"
_401_BODY = '{"errors": {"detail": "Authentication credentials were not provided."}}'


def _ok_page(record_id: int = 1) -> HttpResponse:
    record = {
        "type": "ServiceGroup",
        "id": record_id,
        "attributes": {"created": "2026-01-01T00:00:00.000000+0000", "updated": "2026-01-02T00:00:00.000000+0000", "name": "g"},
    }
    return HttpResponse(body=json.dumps({"data": [record], "links": {"next": None}}), status_code=200)


def _token_response(access_token: str = "tok", refresh_token: str | None = None) -> dict:
    body = {"access_token": access_token, "expires_in": 3600}
    if refresh_token:
        body["refresh_token"] = refresh_token
    return body


def _read(config: dict, streams: tuple[str, ...] = (_STREAM,)) -> EntrypointOutput:
    catalog = CatalogBuilder()
    for stream in streams:
        catalog = catalog.with_stream(stream, SyncMode.full_refresh)
    return read(get_source(config=config), config=config, catalog=catalog.build(), state=StateBuilder().build())


def _control_messages(stdout: str) -> list[dict]:
    messages = []
    for line in stdout.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("type") == "CONTROL":
            messages.append(message)
    return messages


def _read_with_control_messages(config: dict, streams: tuple[str, ...] = (_STREAM,)) -> tuple[EntrypointOutput, list[dict]]:
    stdout = StringIO()
    with redirect_stdout(stdout):
        output = _read(config, streams)
    return output, _control_messages(stdout.getvalue())


def _token_requests(http_mocker: HttpMocker) -> list:
    return [request for request in http_mocker._mocker.request_history if request.url == _TOKEN_URL]


def _persisted_credentials(control_messages: list[dict]) -> list[dict]:
    return [message["control"]["connectorConfig"]["config"]["credentials"] for message in control_messages]


def test_valid_stored_token_is_used_without_refresh(virtual_clock: list[float]) -> None:
    config = ConfigBuilder().with_oauth_credentials(access_token=_STORED_ACCESS_TOKEN, token_expiry_date=_FUTURE_EXPIRY).build()
    page_request = UptickRequestBuilder.collection(_STREAM, token=_STORED_ACCESS_TOKEN)

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(_TOKEN_URL, json=_token_response())
        http_mocker.get(page_request, _ok_page())
        output, control_messages = _read_with_control_messages(config)

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == [1]
    assert _token_requests(http_mocker) == []
    http_mocker.assert_number_of_calls(page_request, 1)
    assert _persisted_credentials(control_messages) == []


@pytest.mark.parametrize(
    "expired_at",
    [
        pytest.param("2020-01-01T00:00:00Z", id="seconds"),
        pytest.param("2020-01-01T00:00:00.123456Z", id="microseconds"),
        pytest.param("2020-01-01T00:00:00.123456789Z", id="nanoseconds"),
    ],
)
def test_expired_stored_token_refreshes_once_and_writes_back_expiry(expired_at: str, virtual_clock: list[float]) -> None:
    config = ConfigBuilder().with_oauth_credentials(access_token=_STORED_ACCESS_TOKEN, token_expiry_date=expired_at).build()
    page_request = UptickRequestBuilder.collection(_STREAM, token="tok")

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(_TOKEN_URL, json=_token_response("tok"))
        http_mocker.get(page_request, _ok_page())
        output, control_messages = _read_with_control_messages(config)

    assert output.errors == []
    assert len(_token_requests(http_mocker)) == 1
    http_mocker.assert_number_of_calls(page_request, 1)
    persisted = _persisted_credentials(control_messages)
    assert len(persisted) == 1
    assert persisted[0]["access_token"] == "tok"
    assert persisted[0]["refresh_token"] == "test-refresh-token"
    new_expiry = datetime.fromisoformat(persisted[0]["token_expiry_date"].replace("Z", "+00:00"))
    assert new_expiry > datetime.now(timezone.utc)


@pytest.mark.parametrize(
    "status_code,body",
    [
        pytest.param(400, '{"error": "invalid_grant"}', id="invalid_grant"),
        pytest.param(401, '{"error": "invalid_client"}', id="invalid_client"),
    ],
)
def test_rejected_refresh_fails_as_config_error(status_code: int, body: str, virtual_clock: list[float]) -> None:
    config = ConfigBuilder().with_oauth_credentials(access_token=_STORED_ACCESS_TOKEN, token_expiry_date="2020-01-01T00:00:00Z").build()
    page_request = UptickRequestBuilder.collection(_STREAM, token="tok")

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(_TOKEN_URL, text=body, status_code=status_code)
        http_mocker.get(page_request, _ok_page())
        output, control_messages = _read_with_control_messages(config)

    assert output.records == []
    matching = [
        message.trace.error
        for message in output.errors
        if message.trace.error.failure_type == FailureType.config_error
        and "Refresh token was rejected by the OAuth provider" in message.trace.error.message
    ]
    assert len(matching) == 1, f"expected exactly one config_error from the rejected refresh, got {output.errors}"
    assert virtual_clock == []
    assert len(_token_requests(http_mocker)) == 1
    http_mocker.assert_number_of_calls(page_request, 0)
    assert _persisted_credentials(control_messages) == []


def test_stream_401_refresh_persists_rotated_refresh_token(virtual_clock: list[float]) -> None:
    config = ConfigBuilder().with_oauth_credentials(access_token=_STORED_ACCESS_TOKEN, token_expiry_date=_FUTURE_EXPIRY).build()
    stale_page_request = UptickRequestBuilder.collection(_STREAM, token=_STORED_ACCESS_TOKEN)
    refreshed_page_request = UptickRequestBuilder.collection(_STREAM, token="tok2")

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(_TOKEN_URL, json=_token_response("tok2", refresh_token="rotated-refresh-token"))
        http_mocker.get(stale_page_request, HttpResponse(body=_401_BODY, status_code=401))
        http_mocker.get(refreshed_page_request, _ok_page())
        output, control_messages = _read_with_control_messages(config)

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == [1]
    assert len(_token_requests(http_mocker)) == 1
    http_mocker.assert_number_of_calls(stale_page_request, 1)
    http_mocker.assert_number_of_calls(refreshed_page_request, 1)
    persisted = _persisted_credentials(control_messages)
    assert len(persisted) == 1
    assert persisted[0]["access_token"] == "tok2"
    assert persisted[0]["refresh_token"] == "rotated-refresh-token"


def test_two_streams_needing_refresh_share_one_token_request(virtual_clock: list[float]) -> None:
    config = ConfigBuilder().with_oauth_credentials(access_token=_STORED_ACCESS_TOKEN, token_expiry_date="2020-01-01T00:00:00Z").build()
    streams = (_STREAM, "accreditationtypes")

    with HttpMocker() as http_mocker:
        http_mocker._mocker.post(_TOKEN_URL, json=_token_response("tok"))
        for stream in streams:
            http_mocker.get(UptickRequestBuilder.collection(stream, token="tok"), _ok_page())
        output, control_messages = _read_with_control_messages(config, streams=streams)

    assert output.errors == []
    for stream in streams:
        assert output.get_stream_statuses(stream)[-1].name == "COMPLETE"
    assert len(_token_requests(http_mocker)) == 1
    assert len(_persisted_credentials(control_messages)) == 1
