# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import timedelta

import pytest
import requests
from _helpers import CONFIG, USER, collection, list_request, read_stream, request
from conftest import get_source

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.call_rate import CallRateLimitHit, HttpAPIBudget, MovingWindowCallRatePolicy
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def budget() -> HttpAPIBudget:
    source = get_source(CONFIG)
    source.streams(CONFIG)
    return source._constructor._api_budget


def prepared(path: str = "users/me") -> requests.PreparedRequest:
    return requests.Request("GET", f"https://api.calendly.com/{path}").prepare()


def test_budget_is_one_500_per_minute_moving_window_policy() -> None:
    actual = budget()
    assert isinstance(actual, HttpAPIBudget)
    policy = actual.get_matching_policy(prepared())
    assert isinstance(policy, MovingWindowCallRatePolicy)
    for path in [
        "users/me",
        "event_types",
        "groups",
        "organization_memberships",
        "scheduled_events",
        "scheduled_events/event/invitees",
    ]:
        assert actual.get_matching_policy(prepared(path)) is policy
    assert actual.get_matching_policy(requests.Request("GET", "https://example.com/users/me").prepare()) is None


def test_five_hundred_and_first_call_is_blocked() -> None:
    actual = budget()
    for _ in range(500):
        actual.acquire_call(prepared(), block=False)
    with pytest.raises(CallRateLimitHit) as error:
        actual.acquire_call(prepared(), block=False)
    assert timedelta(0) < error.value.time_to_wait <= timedelta(minutes=1)


def test_zero_remaining_header_blocks_the_next_call() -> None:
    actual = budget()
    response = requests.Response()
    response.status_code = 200
    response.headers.update({"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "60"})
    actual.update_from_response(prepared(), response)
    with pytest.raises(CallRateLimitHit) as error:
        actual.acquire_call(prepared(), block=False)
    assert timedelta(0) < error.value.time_to_wait <= timedelta(minutes=1)


def test_zero_remaining_makes_the_next_request_wait_a_minute(recorded_sleeps) -> None:
    with HttpMocker() as http:
        http.get(
            request("users/me"), HttpResponse(body=json.dumps({"resource": USER}), status_code=200, headers={"X-RateLimit-Remaining": "0"})
        )
        http.get(list_request("groups"), collection([{"uri": "https://api.calendly.com/groups/1"}]))
        output = read_stream("groups")
        assert not output.errors
        assert len(output.records) == 1
        assert recorded_sleeps == [60.0]


@pytest.mark.parametrize("workers, expected", [(None, 4), (2, 2), (7, 7), (10, 10)])
def test_concurrency_uses_configured_workers(workers: int | None, expected: int) -> None:
    config = {**CONFIG, **({"num_workers": workers} if workers is not None else {})}
    with HttpMocker() as http:
        target = request("users/me")
        http.get(target, HttpResponse(body=json.dumps({"resource": USER}), status_code=200))
        output = read_stream("api_user", config)
        assert not output.errors
        assert [record.record.data for record in output.records] == [USER]
        http.assert_number_of_calls(target, 1)
    assert get_source(config)._concurrent_source._threadpool._threadpool._max_workers == expected


@pytest.mark.parametrize("workers, reason", [(1, "1 is less than the minimum of 2"), (11, "11 is greater than the maximum of 10")])
def test_concurrency_rejects_out_of_bounds_config_before_requests(workers: int, reason: str) -> None:
    with HttpMocker() as http:
        target = request("users/me")
        http.get(target, HttpResponse(body=json.dumps({"resource": USER}), status_code=200))
        output = read_stream("api_user", {**CONFIG, "num_workers": workers})
        assert not output.records
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == f"Config validation error: {reason}"
        http.assert_number_of_calls(target, 0)
