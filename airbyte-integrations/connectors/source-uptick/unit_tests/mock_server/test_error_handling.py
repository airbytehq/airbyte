# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server coverage for the shared `error_handler` in `manifest.yaml`.

Every JSON:API stream goes through the same `DefaultErrorHandler`, so a single collection stream is
enough to lock in: fail-fast `config_error` on 401/403 with the connector's own messages, `Retry-After`
honoured on 429, the 1800s `Retry-After` cap, and 5xx exhaustion surfacing as a non-config failure.
"""

import json
from unittest.mock import patch

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import UptickRequestBuilder


_STREAM = "servicegroups"
_TOKEN_REQUEST = HttpRequest(
    url=UptickRequestBuilder.token_endpoint(),
    body="grant_type=password&client_id=test-client-id&client_secret=test-client-secret&username=test-user&password=test-password",
)
_TOKEN_RESPONSE = HttpResponse(body=json.dumps({"access_token": "tok", "expires_in": 3600}), status_code=200)
_401_MESSAGE = "HTTP 401: Uptick rejected the client credentials or user login."
_403_MESSAGE = "HTTP 403: Uptick user lacks permission for the requested endpoint."
_RETRY_AFTER_CAP_SECONDS = 1800
_PAGE_REQUEST = UptickRequestBuilder.collection(_STREAM)


def _ok_page(record_id: int) -> HttpResponse:
    record = {
        "type": "ServiceGroup",
        "id": record_id,
        "attributes": {"created": "2026-01-01T00:00:00.000000+0000", "updated": "2026-01-02T00:00:00.000000+0000", "name": "g"},
    }
    return HttpResponse(body=json.dumps({"data": [record], "links": {"next": None}}), status_code=200)


def _read_with_responses(responses: list[HttpResponse]) -> tuple[EntrypointOutput, list[float], HttpMocker]:
    sleeps: list[float] = []
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
        http_mocker.get(_PAGE_REQUEST, responses)
        with patch("time.sleep", sleeps.append):
            output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())
    return output, sleeps, http_mocker


def _stream_errors(output: EntrypointOutput) -> list:
    return [message.trace.error for message in output.errors if message.trace.stream_status is None]


@pytest.mark.parametrize(
    "status_code,message",
    [
        pytest.param(401, _401_MESSAGE, id="401_config_error"),
        pytest.param(403, _403_MESSAGE, id="403_config_error"),
    ],
)
def test_auth_errors_fail_fast_without_retry(status_code: int, message: str) -> None:
    output, sleeps, http_mocker = _read_with_responses([HttpResponse(body='{"detail": "nope"}', status_code=status_code)])

    assert output.records == []
    assert output.get_stream_statuses(_STREAM)[-1].name == "INCOMPLETE"
    matching = [error for error in _stream_errors(output) if error.message == message]
    assert len(matching) == 1, f"expected exactly one error with the connector message, got {output.errors}"
    assert matching[0].failure_type == FailureType.config_error
    assert sleeps == []
    http_mocker.assert_number_of_calls(_TOKEN_REQUEST, 1)
    http_mocker.assert_number_of_calls(_PAGE_REQUEST, 1)


def test_429_waits_for_retry_after_then_succeeds() -> None:
    output, sleeps, http_mocker = _read_with_responses(
        [
            HttpResponse(body='{"detail": "throttled"}', status_code=429, headers={"Retry-After": "7"}),
            _ok_page(1),
        ]
    )

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == [1]
    assert sleeps and max(sleeps) >= 7, f"Retry-After was not honoured: {sleeps}"
    http_mocker.assert_number_of_calls(_PAGE_REQUEST, 2)


def test_429_retry_after_at_cap_fails_instead_of_waiting() -> None:
    output, sleeps, _ = _read_with_responses(
        [HttpResponse(body='{"detail": "throttled"}', status_code=429, headers={"Retry-After": str(_RETRY_AFTER_CAP_SECONDS)})]
    )

    assert output.records == []
    assert output.get_stream_statuses(_STREAM)[-1].name == "INCOMPLETE"
    assert any(error.failure_type == FailureType.transient_error for error in _stream_errors(output)), output.errors
    assert all(duration < _RETRY_AFTER_CAP_SECONDS for duration in sleeps), f"waited at or above the cap: {sleeps}"


def test_5xx_exhausts_retries_without_auth_message() -> None:
    output, _, http_mocker = _read_with_responses([HttpResponse(body="", status_code=503, headers={"Retry-After": "0"}) for _ in range(6)])

    assert output.records == []
    assert output.get_stream_statuses(_STREAM)[-1].name == "INCOMPLETE"
    errors = _stream_errors(output)
    assert any("Exhausted available request attempts" in error.message for error in errors), output.errors
    assert not any(error.message in {_401_MESSAGE, _403_MESSAGE} for error in errors), output.errors
    http_mocker.assert_number_of_calls(_PAGE_REQUEST, 6)
