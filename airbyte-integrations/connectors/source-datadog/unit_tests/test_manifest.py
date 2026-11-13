# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from collections.abc import Mapping
from typing import Any

import pytest
import requests

from airbyte_cdk.sources.declarative.concurrency_level import ConcurrencyLevel
from airbyte_cdk.sources.streams.call_rate import HttpRequestRegexMatcher
from unit_tests.conftest import CONFIG, get_source


STREAMS = [
    "audit_logs",
    "dashboards",
    "downtimes",
    "incident_teams",
    "incidents",
    "logs",
    "metrics",
    "monitors",
    "service_level_objectives",
    "synthetic_tests",
    "users",
]

# https://docs.datadoghq.com/getting_started/site/
DATADOG_SITES = [
    "datadoghq.com",
    "us3.datadoghq.com",
    "us5.datadoghq.com",
    "datadoghq.eu",
    "ddog-gov.com",
    "us2.ddog-gov.com",
    "ap1.datadoghq.com",
    "ap2.datadoghq.com",
    "uk1.datadoghq.com",
]

# The limit and period Datadog reported in its X-RateLimit headers on 2026-11-12, and on 2026-11-13 for the audit events.
RATE_LIMITS = {
    "/api/v2/audit/events": {"limit": 100, "interval": "PT60S"},
    "/api/v1/dashboard": {"limit": 60, "interval": "PT60S"},
    "/api/v1/downtime": {"limit": 60, "interval": "PT60S"},
    "/api/v2/incidents": {"limit": 100, "interval": "PT60S"},
    "/api/v2/logs/events": {"limit": 300, "interval": "PT60S"},
    "/api/v2/metrics": {"limit": 50, "interval": "PT10S"},
    "/api/v1/monitor": {"limit": 1000, "interval": "PT10S"},
    "/api/v1/slo": {"limit": 1000, "interval": "PT10S"},
    "/api/v1/synthetics/tests": {"limit": 12000, "interval": "PT60S"},
}
PATHS_WITHOUT_A_KNOWN_LIMIT = ["/api/v2/teams", "/api/v2/users"]


def _rates_that_apply_to(path: str) -> list[list[Mapping[str, Any]]]:
    request = requests.Request("GET", f"https://api.{CONFIG['site']}{path}").prepare()
    return [
        policy["rates"]
        for policy in get_source().resolved_manifest["api_budget"]["policies"]
        if any(HttpRequestRegexMatcher(url_path_pattern=matcher["url_path_pattern"])(request) for matcher in policy["matchers"])
    ]


def test_manifest_loads_on_the_pinned_cdk_and_lists_every_stream() -> None:
    streams = get_source().streams(CONFIG)

    assert sorted(stream.name for stream in streams) == sorted(STREAMS)


def test_site_offers_every_datadog_site() -> None:
    spec = get_source().spec(logging.getLogger("airbyte"))

    site = spec.connectionSpecification["properties"]["site"]
    assert sorted(site["enum"]) == sorted(DATADOG_SITES)


def test_num_workers_is_in_the_spec_with_its_bounds() -> None:
    spec = get_source().spec(logging.getLogger("airbyte"))

    num_workers = spec.connectionSpecification["properties"]["num_workers"]
    assert {key: num_workers[key] for key in ("type", "default", "minimum", "maximum")} == {
        "type": "integer",
        "default": 3,
        "minimum": 2,
        "maximum": 10,
    }
    assert "num_workers" not in spec.connectionSpecification["required"]


@pytest.mark.parametrize(
    ("config", "workers"),
    [
        pytest.param({}, 3, id="default"),
        pytest.param({"num_workers": 2}, 2, id="configured"),
        pytest.param({"num_workers": 50}, 10, id="capped"),
    ],
)
def test_concurrency_follows_num_workers(config: Mapping[str, Any], workers: int) -> None:
    definition = get_source().resolved_manifest["concurrency_level"]

    concurrency_level = ConcurrencyLevel(
        default_concurrency=definition["default_concurrency"],
        max_concurrency=definition["max_concurrency"],
        config=config,
        parameters={},
    )

    assert concurrency_level.get_concurrency_level() == workers


@pytest.mark.parametrize("stream", STREAMS)
def test_every_stream_keeps_the_shared_retries_and_backoff(stream: str) -> None:
    streams = {definition["name"]: definition for definition in get_source().resolved_manifest["streams"]}

    error_handler = streams[stream]["retriever"]["requester"]["error_handler"]

    assert (error_handler["type"], error_handler["max_retries"]) == ("DefaultErrorHandler", 5)
    assert [(strategy["type"], strategy.get("header"), strategy.get("factor")) for strategy in error_handler["backoff_strategies"]] == [
        ("WaitTimeFromHeader", "X-RateLimit-Reset", None),
        ("ExponentialBackoffStrategy", None, 5),
    ]


@pytest.mark.parametrize("path", RATE_LIMITS)
def test_api_budget_has_one_policy_for_each_rate_limited_path(path: str) -> None:
    assert _rates_that_apply_to(path) == [[RATE_LIMITS[path]]]


@pytest.mark.parametrize("path", PATHS_WITHOUT_A_KNOWN_LIMIT)
def test_api_budget_leaves_the_other_paths_alone(path: str) -> None:
    assert _rates_that_apply_to(path) == []


def test_api_budget_reads_the_calls_left_from_datadog() -> None:
    budget = get_source().resolved_manifest["api_budget"]

    assert budget["ratelimit_remaining_header"] == "X-RateLimit-Remaining"
    # X-RateLimit-Reset holds the seconds until the reset, and the CDK would read it as a point in time.
    assert "ratelimit_reset_header" not in budget
