# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Regression tests for the reporting endpoint API budget and daily-quota pacing."""

import time

import pytest
from requests import Request
from unit_tests.conftest import get_source

from airbyte_cdk.sources.streams.call_rate import CallRateLimitHit
from mock_server.config import ConfigBuilder


_BASE_URL = "https://a.klaviyo.com/api"
_REPORT_ENDPOINTS = ("flow-series-reports", "campaign-values-reports")


def _report_policy(endpoint: str):
    config = ConfigBuilder().build()
    source = get_source(config=config)
    api_budget_model = source._source_config.get("api_budget")
    assert api_budget_model, f"Could not find the parsed API budget while looking up {endpoint}"
    source._constructor.set_api_budget(api_budget_model, config)
    api_budget = source._constructor._api_budget
    assert api_budget is not None, f"Could not construct the API budget while looking up {endpoint}"
    request = Request("POST", f"{_BASE_URL}/{endpoint}").prepare()
    matching_policies = [policy for policy in api_budget._policies if policy.matches(request)]
    assert len(matching_policies) == 1, (
        f"Expected one API-budget policy matching POST /api/{endpoint}, "
        f"found {len(matching_policies)}"
    )
    return matching_policies[0], request


@pytest.mark.parametrize("endpoint", _REPORT_ENDPOINTS)
def test_report_endpoint_budget_stays_within_daily_quota(endpoint: str):
    policy, _ = _report_policy(endpoint)
    rates = policy._bucket.rates

    max_daily_throughput = min(
        rate.limit * 86400 / (rate.interval / 1000) for rate in rates
    )

    assert max_daily_throughput <= 225, (
        f"{endpoint} budget allows {max_daily_throughput:.2f} calls/day, "
        f"above Klaviyo's documented 225/day quota; rates: {rates}"
    )
    max_interval = max(rate.interval / 1000 for rate in rates)
    assert max_interval <= 600, (
        f"{endpoint} budget has a {max_interval:.2f}s interval; intervals over 600s "
        f"are forbidden because they can cause multi-hour local sleeps; rates: {rates}"
    )


@pytest.mark.parametrize("endpoint", _REPORT_ENDPOINTS)
def test_report_endpoint_budget_paces_requests(endpoint: str):
    policy, request = _report_policy(endpoint)
    policy.try_acquire(request, weight=1)

    # pyrate_limiter uses its own clock, so freezegun does not affect this wait.
    time.sleep(1.1)

    with pytest.raises(CallRateLimitHit) as raised:
        policy.try_acquire(request, weight=1)

    time_to_wait = raised.value.time_to_wait.total_seconds()
    assert 60 < time_to_wait <= 600, (
        f"{endpoint} pacing wait was {time_to_wait:.2f}s; expected 60s < wait <= 600s "
        "to prove the sustainable reporting rate is enforced without a multi-hour wait"
    )
