#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import time

import pytest

from airbyte_cdk.sources.streams.call_rate import APIBudget, CallRatePolicy, Duration, HttpRequestMatcher, Rate, CallRateLimitHit
from requests import Request


def test_http_mapping():
    api_budget = APIBudget()
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/users", method="GET"),
        policy=CallRatePolicy(
            rates=[
                Rate(10, Duration.MINUTE),
                Rate(100, Duration.HOUR),
            ],
        ),
    )
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/groups", method="POST"),
        policy=CallRatePolicy(
            rates=[
                Rate(1, Duration.MINUTE),
            ],
        ),
    )

    api_budget.acquire_call(Request("POST", url="/unmatched_endpoint"), block=False), "unrestricted call"
    api_budget.acquire_call(Request("GET", url="/users"), block=False), "first call"
    api_budget.acquire_call(Request("GET", url="/users"), block=False), "second call"

    for i in range(8):
        api_budget.acquire_call(Request("GET", url="/users"), block=False), f"{i + 3} call"

    with pytest.raises(CallRateLimitHit) as excinfo:
        api_budget.acquire_call(Request("GET", url="/users"), block=False), "call over limit"
    assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(60, 0.1)

    time.sleep(5)

    with pytest.raises(CallRateLimitHit) as excinfo:
        api_budget.acquire_call(Request("GET", url="/users"), block=False), "call over limit"
    assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(60 - 5, 0.1)

    api_budget.acquire_call(Request("POST", url="/groups"), block=False), "doesn't affect other policies"
    api_budget.acquire_call(Request("POST", url="/list"), block=False), "unrestricted call"
