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
    stream_name = endpoint.replace("-", "_")
    stream = next(stream for stream in source.streams(config) if stream.name == stream_name)
    requester = stream._stream_partition_generator._partition_factory._retriever.requester
    api_budget = requester._http_client._api_budget
    request = Request("POST", f"{_BASE_URL}/{endpoint}").prepare()
    matching_policies = [policy for policy in api_budget._policies if policy.matches(request)]
    assert len(matching_policies) == 1
    return matching_policies[0], request


@pytest.mark.parametrize("endpoint", _REPORT_ENDPOINTS)
def test_report_endpoint_budget_stays_within_daily_quota(endpoint: str):
    policy, _ = _report_policy(endpoint)
    rates = policy._bucket.rates

    max_daily_throughput = min(
        rate.limit * 86400 / (rate.interval / 1000) for rate in rates
    )

    assert max_daily_throughput <= 225
    assert all(rate.interval / 1000 <= 600 for rate in rates)


@pytest.mark.parametrize("endpoint", _REPORT_ENDPOINTS)
def test_report_endpoint_budget_paces_requests(endpoint: str):
    policy, request = _report_policy(endpoint)
    policy.try_acquire(request, weight=1)

    # pyrate_limiter uses its own clock, so freezegun does not affect this wait.
    time.sleep(1.1)

    with pytest.raises(CallRateLimitHit) as raised:
        policy.try_acquire(request, weight=1)

    time_to_wait = raised.value.time_to_wait.total_seconds()
    assert 60 < time_to_wait <= 600
