# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Mapping

import pytest
import requests
import yaml
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG: Mapping[str, Any] = {
    "tenant_id": "test-tenant",
    "start_date": "2024-01-01T00:00:00Z",
    "credentials": {
        "auth_type": "oauth2_access_token",
        "access_token": "test-token",
    },
}
BASE_URL = "https://api.xero.com/api.xro/2.0/"
STREAM_NAME = "currencies"


@pytest.fixture(autouse=True)
def record_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    sleep_durations: list[float] = []
    monkeypatch.setattr("time.sleep", sleep_durations.append)
    return sleep_durations


def request() -> HttpRequest:
    return HttpRequest(
        url=f"{BASE_URL}Currencies",
        query_params={"page": "1", "pageSize": "1000"},
    )


def http_response(body: Mapping[str, Any], status_code: int = 200, headers: Mapping[str, str] | None = None) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code, headers=headers or {})


def read_currencies(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(STREAM_NAME, SyncMode.full_refresh).build()
    source = get_source(CONFIG, catalog)
    return read(source, CONFIG, catalog, expecting_exception=expecting_exception)


@pytest.mark.parametrize("problem", ["day", "Day"])
def test_daily_rate_limit_fails_without_retry(problem: str) -> None:
    stream_request = request()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            stream_request,
            http_response(
                {},
                status_code=429,
                headers={"X-Rate-Limit-Problem": problem, "Retry-After": "40000"},
            ),
        )
        output = read_currencies(expecting_exception=True)
        http_mocker.assert_number_of_calls(stream_request, 1)

    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.transient_error
    assert "Xero daily API call limit is reached" in error.message


def test_unauthorized_credentials_fail_with_actionable_message() -> None:
    stream_request = request()
    with HttpMocker() as http_mocker:
        http_mocker.get(stream_request, http_response({}, status_code=401))
        output = read_currencies(expecting_exception=True)
        http_mocker.assert_number_of_calls(stream_request, 1)

    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "Xero rejected the access credentials" in error.message


def test_forbidden_response_is_ignored() -> None:
    stream_request = request()
    with HttpMocker() as http_mocker:
        http_mocker.get(stream_request, http_response({}, status_code=403))
        output = read_currencies()
        http_mocker.assert_number_of_calls(stream_request, 1)

    assert output.records == []
    assert output.errors == []


def test_minute_rate_limit_retries_and_reads_records(record_sleep: list[float]) -> None:
    stream_request = request()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            stream_request,
            [
                http_response(
                    {},
                    status_code=429,
                    headers={"X-Rate-Limit-Problem": "minute", "Retry-After": "7"},
                ),
                http_response({"Currencies": [{"Code": "USD", "Description": "US Dollar"}]}),
            ],
        )
        output = read_currencies()
        http_mocker.assert_number_of_calls(stream_request, 2)

    assert [record.record.data["Code"] for record in output.records] == ["USD"]
    assert output.errors == []
    if record_sleep:
        assert any(duration >= 7 for duration in record_sleep)


def response(status_code: int, headers: Mapping[str, str] | None = None) -> requests.Response:
    result = requests.Response()
    result.status_code = status_code
    result._content = b"{}"
    result.headers.update(headers or {})
    result.url = f"{BASE_URL}Currencies"
    return result


def build_error_handler() -> DefaultErrorHandler:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    handler_definition = manifest["definitions"]["base_requester"]["error_handler"]
    return ModelToComponentFactory().create_component(
        DefaultErrorHandlerModel,
        handler_definition,
        config={},
    )


def select_backoff(handler: DefaultErrorHandler, response: requests.Response) -> float | None:
    for strategy in handler.backoff_strategies:
        backoff_time = strategy.backoff_time(response_or_exception=response, attempt_count=1)
        if backoff_time:
            return backoff_time
    return None


def test_minute_rate_limit_uses_retry_action_and_retry_after_backoff() -> None:
    handler = build_error_handler()
    rate_limit_response = response(429, {"X-Rate-Limit-Problem": "minute", "Retry-After": "7"})

    result = handler.interpret_response(rate_limit_response)

    assert result.response_action.name == "RETRY"
    assert select_backoff(handler, rate_limit_response) == 7.0


def test_rate_limit_without_retry_after_uses_exponential_backoff() -> None:
    handler = build_error_handler()
    rate_limit_response = response(429, {"X-Rate-Limit-Problem": "minute"})

    result = handler.interpret_response(rate_limit_response)

    assert result.response_action.name == "RETRY"
    assert select_backoff(handler, rate_limit_response) == 2 * 2**1
    assert handler.max_retries == 5
