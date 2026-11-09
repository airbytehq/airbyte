# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import NOW, error, list_request, page, record, run


@pytest.mark.parametrize(
    "status,error_type,expected",
    [
        (401, "unauthorized", "Recurly rejected the API key"),
        (403, "forbidden", "Recurly denied access"),
    ],
)
@freeze_time(NOW)
def test_auth_failures_are_actionable_config_errors(status, error_type, expected):
    with HttpMocker() as mocker:
        request = list_request("plans")
        mocker.get(request, error(status, error_type))
        output = run("plans", expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
    assert output.records == []
    failures = [message.trace.error for message in output.errors]
    assert any(failure.failure_type == FailureType.config_error and expected in failure.message for failure in failures)


def test_rate_limited_request_waits_until_the_reset_header_then_retries():
    reset_epoch = 1768435260  # 2026-01-15T00:01:00Z, 60 seconds after NOW
    with freeze_time(NOW) as clock, HttpMocker() as mocker, patch("time.sleep", side_effect=lambda seconds: clock.tick(seconds)) as sleep:
        request = list_request("plans")
        mocker.get(
            request,
            [
                error(429, "rate_limited", headers={"X-RateLimit-Reset": str(reset_epoch), "X-RateLimit-Remaining": "0"}),
                page([record("plan-1", "2026-01-02T00:00:00Z")]),
            ],
        )
        output = run("plans")
        mocker.assert_number_of_calls(request, 2)
    assert [message.record.data["id"] for message in output.records] == ["plan-1"]
    assert output.errors == []
    waits = [call.args[0] for call in sleep.call_args_list if call.args and call.args[0]]
    assert waits[0] == 61.0, waits


@freeze_time(NOW)
def test_server_errors_retry_with_exponential_backoff_then_succeed():
    with HttpMocker() as mocker, patch("time.sleep") as sleep:
        request = list_request("plans")
        mocker.get(request, [error(503, "unavailable"), error(503, "unavailable"), page([record("plan-1", "2026-01-02T00:00:00Z")])])
        output = run("plans")
        mocker.assert_number_of_calls(request, 3)
    assert [message.record.data["id"] for message in output.records] == ["plan-1"]
    waits = [call.args[0] for call in sleep.call_args_list if call.args and call.args[0]]
    assert waits == [11.0, 21.0], waits
