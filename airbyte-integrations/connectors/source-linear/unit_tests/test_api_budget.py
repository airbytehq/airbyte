# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Unit tests for source-linear API budget configuration.

These tests verify that the declarative source constructs one shared
``HttpAPIBudget`` for the stream requesters, resolves the authentication-tier
rate limits, and safely processes Linear's rate-limit response headers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import requests

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.call_rate import HttpAPIBudget, MovingWindowCallRatePolicy


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
API_KEY_CONFIG: Mapping[str, Any] = {
    "api_key": "test-api-key",
    "start_date": "2024-01-01T00:00:00.000Z",
}
OAUTH_CONFIG: Mapping[str, Any] = {
    "credentials": {
        "auth_type": "OAuth2.0",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
    },
}


def _build_source_and_budget(config: Mapping[str, Any]) -> tuple[YamlDeclarativeSource, HttpAPIBudget]:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=config)
    streams = source.streams(config=config)
    budgets = []
    for stream in streams:
        partition = next(iter(stream.generate_partitions()))
        requester = partition._retriever.requester
        budget = requester._http_client._api_budget
        assert isinstance(budget, HttpAPIBudget)
        budgets.append(budget)

    assert budgets
    assert all(budget is budgets[0] for budget in budgets)
    return source, budgets[0]


def _resolved_rates(config: Mapping[str, Any]) -> list[tuple[int, int]]:
    _, budget = _build_source_and_budget(config)
    assert len(budget._policies) == 1
    policy = budget._policies[0]
    assert isinstance(policy, MovingWindowCallRatePolicy)
    return [(rate.limit, rate.interval // 1000) for rate in policy._bucket.rates]


def test_api_budget_is_constructed_and_wired_to_every_stream_requester() -> None:
    _, budget = _build_source_and_budget(API_KEY_CONFIG)

    assert isinstance(budget._policies[0], MovingWindowCallRatePolicy)
    assert budget._policies[0]._matchers == []


def test_api_key_rates_are_resolved_from_the_manifest() -> None:
    assert _resolved_rates(API_KEY_CONFIG) == [(10, 10), (40, 60), (2500, 3600)]


def test_oauth_rates_are_resolved_from_the_manifest() -> None:
    assert _resolved_rates(OAUTH_CONFIG) == [(20, 10), (80, 60), (5000, 3600)]


def test_linear_rate_limit_headers_do_not_use_the_millisecond_reset_header() -> None:
    _, budget = _build_source_and_budget(API_KEY_CONFIG)

    assert budget._ratelimit_remaining_header == "X-RateLimit-Requests-Remaining"
    # The CDK default, i.e. no Linear reset header is wired in: Linear reports its
    # reset timestamps in epoch milliseconds, which the budget cannot parse.
    assert budget._ratelimit_reset_header == "ratelimit-reset"

    request = requests.Request("POST", "https://api.linear.app/graphql").prepare()
    response = requests.Response()
    response.status_code = 200
    response.headers["X-RateLimit-Requests-Remaining"] = "0"
    response.headers["X-RateLimit-Requests-Reset"] = "1787348400000"

    budget.update_from_response(request, response)
