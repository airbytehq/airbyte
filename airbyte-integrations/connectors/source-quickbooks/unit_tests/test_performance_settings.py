# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the QuickBooks pacing settings: pagination stop condition, rate budget and concurrency."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from requests import Response

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
CONFIG: Mapping[str, Any] = {
    "realm_id": "4620816365287999999",
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "access_token": "test-access-token",
    "token_expiry_date": "2099-01-01T00:00:00Z",
    "start_date": "2024-01-01T00:00:00Z",
    "sandbox": True,
}

# QuickBooks returns at most 1000 rows per query and the manifest asks for MAXRESULTS 200.
EFFECTIVE_MAX_RESULTS = 200


def _source(config: Mapping[str, Any] = CONFIG) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=config)


def _retriever(stream_name: str, config: Mapping[str, Any] = CONFIG) -> Any:
    source = _source(config)
    stream = {stream.name: stream for stream in source.streams(config=config)}[stream_name]
    return next(iter(stream.generate_partitions()))._retriever


def _response_with(record_count: int) -> Response:
    body = {"QueryResponse": {"Invoice": [{"Id": str(index)} for index in range(record_count)]}}
    response = MagicMock(spec=Response)
    response.json.return_value = body
    response.content = json.dumps(body).encode()
    response.text = json.dumps(body)
    return response


@pytest.mark.parametrize(
    "record_count, expected_token",
    [
        pytest.param(EFFECTIVE_MAX_RESULTS, EFFECTIVE_MAX_RESULTS, id="full_page_requests_next_offset"),
        pytest.param(EFFECTIVE_MAX_RESULTS - 1, None, id="short_page_stops_without_extra_request"),
        pytest.param(0, None, id="empty_page_stops"),
    ],
)
def test_pagination_stops_once_a_slice_is_drained(record_count: int, expected_token: Any) -> None:
    """A page smaller than MAXRESULTS must end the slice instead of costing one more empty request."""
    strategy = _retriever("invoices").paginator.pagination_strategy
    response = _response_with(record_count)

    assert strategy.next_page_token(response, record_count, None, None) == expected_token


def test_page_size_matches_the_requested_max_results() -> None:
    strategy = _retriever("invoices").paginator.pagination_strategy
    assert strategy._page_size.eval(CONFIG) == EFFECTIVE_MAX_RESULTS


def test_api_budget_stays_below_intuit_realm_limits() -> None:
    api_budget = _retriever("invoices").requester.api_budget
    assert api_budget._status_codes_for_ratelimit_hit == [429]
    assert len(api_budget._policies) == 1

    # pyrate-limiter expresses the interval in milliseconds.
    limits = {rate.interval: rate.limit for rate in api_budget._policies[0]._bucket.rates}
    # Intuit allows 500 requests/minute and 10 concurrent requests/second per realm.
    assert limits == {1000: 8, 60000: 300}


@pytest.mark.parametrize(
    "num_workers, expected_concurrency",
    [
        pytest.param(None, 4, id="default"),
        pytest.param(8, 8, id="user_tuned"),
    ],
)
def test_concurrency_level(num_workers: int | None, expected_concurrency: int) -> None:
    config = dict(CONFIG)
    if num_workers is not None:
        config["num_workers"] = num_workers

    source = _source(config)
    assert source.resolved_manifest["concurrency_level"]["max_concurrency"] == 10
    assert source._concurrent_source._threadpool._threadpool._max_workers == expected_concurrency


def test_num_workers_is_exposed_in_the_spec() -> None:
    num_workers = _source().spec(logging.getLogger("airbyte")).connectionSpecification["properties"]["num_workers"]
    assert num_workers["default"] == 4
    assert num_workers["maximum"] == 10
