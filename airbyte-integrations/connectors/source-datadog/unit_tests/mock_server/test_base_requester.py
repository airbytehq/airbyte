# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from collections.abc import Callable
from typing import Any
from unittest import mock

import pytest

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import read_stream, stream_errors
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import UNEXPECTED_ERROR_BODIES, DatadogPaginatedResponseBuilder, datadog_error


# The permission is the `x-permission` of the operation the stream calls in Datadog's OpenAPI specs.
# The endpoint of `incident_teams` is not in the specs any more.
STREAMS = [
    ("audit_logs", DatadogRequestBuilder.audit_logs_endpoint, "audit_logs_read"),
    ("dashboards", DatadogRequestBuilder.dashboards_endpoint, "dashboards_read"),
    ("downtimes", DatadogRequestBuilder.downtimes_endpoint, "monitors_read"),
    ("incident_teams", DatadogRequestBuilder.incident_teams_endpoint, None),
    ("incidents", DatadogRequestBuilder.incidents_endpoint, "incident_read"),
    ("logs", DatadogRequestBuilder.logs_endpoint, "logs_read_data"),
    ("metrics", DatadogRequestBuilder.metrics_endpoint, "metrics_read"),
    ("monitors", DatadogRequestBuilder.monitors_endpoint, "monitors_read"),
    ("service_level_objectives", DatadogRequestBuilder.service_level_objectives_endpoint, "slos_read"),
    ("synthetic_tests", DatadogRequestBuilder.synthetic_tests_endpoint, "synthetics_read"),
    ("users", DatadogRequestBuilder.users_endpoint, "user_access_read"),
]
STREAM_IDS = [stream for stream, *_ in STREAMS]
ROOT_LIST_STREAMS = {"downtimes", "monitors"}

# The two `errors` values Datadog answered with a 403 on 2026-11-13: for a key without the permission of the
# endpoint, and for a wrong API key, a wrong application key or a wrong site.
MISSING_PERMISSION = ["Forbidden", "Failed permission authorization checks"]
REJECTED_KEYS = ["Forbidden"]


def _missing_permission_message(permission: str | None, datadog_text: str) -> str:
    if permission is None:
        return (
            f"The Application Key lacks a permission that this stream requires: {datadog_text}. "
            "Grant the missing permission to the Application Key in Datadog."
        )
    return f"The Application Key lacks the {permission} permission: {datadog_text}. Grant {permission} to the Application Key in Datadog."


def _users_request() -> HttpRequest:
    # `users` has no API budget policy, so the error handler is the only thing that waits.
    return DatadogRequestBuilder.users_endpoint().with_query_param("page[size]", 100).build()


def _users_page() -> HttpResponse:
    return DatadogPaginatedResponseBuilder("data").with_records([{"id": "user-1"}]).build()


def _waits(sleep: mock.Mock) -> list[float]:
    return [call.args[0] for call in sleep.call_args_list if call.args[0]]


@pytest.mark.parametrize(("stream", "endpoint"), [(stream, endpoint) for stream, endpoint, _ in STREAMS], ids=STREAM_IDS)
def test_every_stream_sends_both_keys(stream: str, endpoint: Callable[[], DatadogRequestBuilder]) -> None:
    empty_answer = "[]" if stream in ROOT_LIST_STREAMS else "{}"
    with HttpMocker() as http_mocker:
        http_mocker.get(endpoint().with_any_query_params().build(), HttpResponse(empty_answer))

        output = read_stream(stream)

    assert output.errors == []


@pytest.mark.parametrize(("stream", "endpoint", "permission"), STREAMS, ids=STREAM_IDS)
def test_missing_permission_names_the_permission_and_not_the_keys(
    stream: str, endpoint: Callable[[], DatadogRequestBuilder], permission: str | None
) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(endpoint().with_any_query_params().build(), datadog_error(403, MISSING_PERMISSION))

        output = read_stream(stream, expecting_error=True)

    errors = stream_errors(output, stream)
    assert errors
    assert {error.failure_type for error in errors} == {FailureType.config_error}
    assert {error.message for error in errors} == {
        _missing_permission_message(permission, "Forbidden, Failed permission authorization checks")
    }


@pytest.mark.parametrize(("stream", "endpoint"), [(stream, endpoint) for stream, endpoint, _ in STREAMS], ids=STREAM_IDS)
def test_any_other_403_names_the_keys_and_not_a_permission(stream: str, endpoint: Callable[[], DatadogRequestBuilder]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(endpoint().with_any_query_params().build(), datadog_error(403, REJECTED_KEYS))

        output = read_stream(stream, expecting_error=True)

    errors = stream_errors(output, stream)
    assert errors
    assert {error.failure_type for error in errors} == {FailureType.config_error}
    assert {error.message for error in errors} == {
        "Datadog rejected the API Key or the Application Key: Forbidden. "
        "Check that both keys are complete and valid and belong to the selected Site."
    }


@pytest.mark.parametrize("body", UNEXPECTED_ERROR_BODIES.values(), ids=UNEXPECTED_ERROR_BODIES.keys())
def test_rejected_keys_message_survives_an_unexpected_body(body: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_users_request(), HttpResponse(body, 403))

        output = read_stream("users", expecting_error=True)

    assert [error.message for error in stream_errors(output, "users")] == [
        "Datadog rejected the API Key or the Application Key. "
        "Check that both keys are complete and valid and belong to the selected Site."
    ]


@pytest.mark.parametrize(
    "errors",
    [
        pytest.param("Failed permission authorization checks", id="errors-is-one-string"),
        pytest.param([{"detail": "Forbidden"}, 403, "Failed permission authorization checks"], id="errors-with-other-values"),
    ],
)
def test_missing_permission_is_found_in_an_unusual_errors_value(errors: Any) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_users_request(), HttpResponse(json.dumps({"errors": errors}), 403))

        output = read_stream("users", expecting_error=True)

    assert [error.message for error in stream_errors(output, "users")] == [
        _missing_permission_message("user_access_read", "Failed permission authorization checks")
    ]


def test_reads_a_page_whose_record_quotes_the_permission_text() -> None:
    # The missing-permission filter matches on the body alone, and the CDK asks every filter about every answer.
    monitor = {"id": 1, "message": "Runbook for 'Failed permission authorization checks': rotate the key."}
    with HttpMocker() as http_mocker:
        http_mocker.get(DatadogRequestBuilder.monitors_endpoint().build(), HttpResponse(json.dumps([monitor])))

        output = read_stream("monitors")

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == [1]


def test_a_malformed_key_gets_the_keys_message() -> None:
    # Datadog answers 401 for a key that is too short or not hexadecimal, and 403 for a well-formed key that is wrong.
    with HttpMocker() as http_mocker:
        http_mocker.get(_users_request(), datadog_error(401, ["Unauthorized"]))

        output = read_stream("users", expecting_error=True)

    errors = stream_errors(output, "users")
    assert [(error.failure_type, error.message) for error in errors] == [
        (
            FailureType.config_error,
            "Datadog rejected the API Key or the Application Key: Unauthorized. "
            "Check that both keys are complete and valid and belong to the selected Site.",
        )
    ]


def test_waits_for_the_rate_limit_reset_and_reads_on() -> None:
    request = _users_request()
    with HttpMocker() as http_mocker, mock.patch("time.sleep") as sleep:
        http_mocker.get(request, [datadog_error(429, ["Too many requests"], {"X-RateLimit-Reset": "7"}), _users_page()])

        output = read_stream("users")

        http_mocker.assert_number_of_calls(request, 2)
    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["user-1"]
    # The CDK adds one second to the wait the header asks for.
    assert _waits(sleep) == [8]


def test_gives_up_on_a_persistent_429_after_five_retries() -> None:
    request = _users_request()
    with HttpMocker() as http_mocker, mock.patch("time.sleep") as sleep:
        http_mocker.get(request, datadog_error(429, ["Too many requests"], {"X-RateLimit-Reset": "7"}))

        output = read_stream("users", expecting_error=True)

        http_mocker.assert_number_of_calls(request, 6)
    errors = stream_errors(output, "users")
    assert [(error.failure_type, error.message) for error in errors] == [(FailureType.transient_error, "API rate limit exceeded.")]
    assert _waits(sleep) == [8] * 5


def test_retries_a_500() -> None:
    request = _users_request()
    with HttpMocker() as http_mocker, mock.patch("time.sleep") as sleep:
        http_mocker.get(request, [datadog_error(500, ["Internal Server Error"]), _users_page()])

        output = read_stream("users")

        http_mocker.assert_number_of_calls(request, 2)
    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["user-1"]
    # The first exponential wait is the factor of 5 times two, plus the CDK's one second.
    assert _waits(sleep) == [11]


def test_reads_with_two_workers() -> None:
    config = ConfigBuilder().with_num_workers(2).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(_users_request(), _users_page())

        output = read_stream("users", config=config)

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["user-1"]
