#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Unit tests for configurable API rate limits and concurrency."""

from typing import Any, Mapping

from _helpers import get_source

from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    ConcurrencyLevel as ConcurrencyLevelModel,
)
from airbyte_cdk.sources.streams.call_rate import MovingWindowCallRatePolicy


def _get_budget_and_concurrency(config: Mapping[str, Any]):
    source = get_source(config=config)
    source.streams(config)
    budget = source._constructor._api_budget
    concurrency = source._constructor.create_component(
        model_type=ConcurrencyLevelModel,
        component_definition=source._source_config["concurrency_level"],
        config=config,
    )
    return budget, concurrency


def _get_rate_limit(budget) -> tuple[int, int]:
    policy = budget._policies[0]
    assert isinstance(policy, MovingWindowCallRatePolicy)
    rate = policy._bucket.rates[0]
    return rate.limit, rate.interval


def test_default_rate_limit_and_concurrency(config):
    budget, concurrency = _get_budget_and_concurrency(config)
    rate_limit, interval = _get_rate_limit(budget)

    assert rate_limit == 30
    assert interval == 60_000
    assert concurrency.get_concurrency_level() == 2


def test_configured_rate_limit_and_concurrency(config):
    config = {**config, "requests_per_minute": 5, "num_workers": 1}
    budget, concurrency = _get_budget_and_concurrency(config)
    rate_limit, interval = _get_rate_limit(budget)

    assert rate_limit == 5
    assert interval == 60_000
    assert concurrency.get_concurrency_level() == 1
