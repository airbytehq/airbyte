# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the When I Work error handlers declared in `manifest.yaml`.

Every stream shares one `DefaultErrorHandler` that retries a 429 up to three times with a 5-second
constant backoff. `payrolls_notices` adds a filter that fails a 401 as a config error with an
actionable message.
"""

import json

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_CONFIG = {"email": "user@example.com", "password": "password"}
_LOGIN_URL = "https://api.login.wheniwork.com/login"
_API_URL = "https://api.wheniwork.com/2/"

_STREAM_PATHS = {
    "account": "account",
    "payrolls": "payrolls",
    "users": "users",
    "timezones": "timezones",
    "payrolls_notices": "payrolls/notices",
    "times": "times",
    "requests": "requests",
    "blocks": "blocks",
    "sites": "sites",
    "locations": "locations",
    "positions": "positions",
    "openshiftapprovalrequests": "openshiftapprovalrequests",
}

_PAYROLLS_NOTICES_401_MESSAGE = (
    "When I Work rejected the payroll notices request as unauthorized. "
    "Check that the email and password are correct and that the account can access payroll notices."
)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Skip real waits and record the requested durations."""
    slept = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _stream_request(stream_name: str) -> HttpRequest:
    return HttpRequest(url=f"{_API_URL}{_STREAM_PATHS[stream_name]}", query_params=ANY_QUERY_PARAMS)


def _mock_login(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        HttpRequest(url=_LOGIN_URL, body=json.dumps(_CONFIG)), HttpResponse(body=json.dumps({"token": "session-token"}), status_code=200)
    )


def _read(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog, expecting_exception=True)


def _error_trace(output: EntrypointOutput):
    """Return the stream-level error trace (the last trace is the aggregated 'streams did not sync' summary)."""
    assert output.errors, "expected the sync to emit an error trace message"
    return output.errors[0].trace.error


def test_manifest_has_no_composite_error_handler() -> None:
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "CompositeErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(_resolved_manifest())

    assert not composite_handlers


@pytest.mark.parametrize("stream_name", sorted(_STREAM_PATHS))
def test_each_stream_uses_a_single_default_error_handler(stream_name: str) -> None:
    error_handler = _resolved_manifest()["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"
    assert error_handler["max_retries"] == 3
    assert error_handler["backoff_strategies"] == [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 5}]


@pytest.mark.parametrize("stream_name", sorted(_STREAM_PATHS))
def test_429_is_retried_three_times_with_5s_backoff_then_fails_as_rate_limited(stream_name: str, no_sleep) -> None:
    with HttpMocker() as http_mocker:
        _mock_login(http_mocker)
        stream_request = _stream_request(stream_name)
        http_mocker.get(stream_request, HttpResponse(body=json.dumps({"error": "Too Many Requests"}), status_code=429))

        output = _read(stream_name)

        http_mocker.assert_number_of_calls(stream_request, 4)

    assert not output.records
    error = _error_trace(output)
    assert error.failure_type == FailureType.transient_error
    assert error.internal_message.endswith("Last exception: Rate limits hit")
    # The CDK adds one second to the configured 5-second constant backoff.
    assert [seconds for seconds in no_sleep if seconds] == [6.0, 6.0, 6.0]


def test_429_then_success_reads_records(no_sleep) -> None:
    with HttpMocker() as http_mocker:
        _mock_login(http_mocker)
        http_mocker.get(
            _stream_request("account"),
            [
                HttpResponse(body=json.dumps({"error": "Too Many Requests"}), status_code=429),
                HttpResponse(body=json.dumps({"account": [{"id": 1}]}), status_code=200),
                HttpResponse(body=json.dumps({"account": []}), status_code=200),
            ],
        )

        output = _read("account")

    assert [record.record.data["id"] for record in output.records] == [1]
    assert not output.errors
    assert [seconds for seconds in no_sleep if seconds] == [6.0]


def test_payrolls_notices_401_fails_as_config_error_without_retry() -> None:
    with HttpMocker() as http_mocker:
        _mock_login(http_mocker)
        stream_request = _stream_request("payrolls_notices")
        http_mocker.get(stream_request, HttpResponse(body=json.dumps({"error": "Unauthorized"}), status_code=401))

        output = _read("payrolls_notices")

        http_mocker.assert_number_of_calls(stream_request, 1)

    assert not output.records
    error = _error_trace(output)
    assert error.failure_type == FailureType.config_error
    assert error.message == _PAYROLLS_NOTICES_401_MESSAGE
