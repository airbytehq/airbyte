#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import time
from pathlib import Path

import pytest
import requests
import yaml
from conftest import get_source

from airbyte_cdk.sources.streams.call_rate import HttpAPIBudget, MovingWindowCallRatePolicy


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_CONFIG = {"api_token": "t", "replication_start_date": "2024-01-01T00:00:00Z"}


def _get_api_budget(config=_CONFIG):
    source = get_source(config)
    # The constructor's api budget is only populated once streams are built.
    streams = source.streams(config)
    return source, streams, source._constructor._api_budget


def test_manifest_declares_api_budget_and_concurrency():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())

    api_budget = manifest["api_budget"]
    assert api_budget["type"] == "HTTPAPIBudget"
    assert api_budget["ratelimit_remaining_header"] == "x-ratelimit-remaining"
    assert api_budget["policies"][0]["type"] == "MovingWindowCallRatePolicy"
    assert api_budget["policies"][0]["rates"][0] == {"limit": 20, "interval": "PT2S"}
    assert api_budget["policies"][0]["matchers"][0]["url_base"] == "https://api.pipedrive.com/"

    concurrency_level = manifest["concurrency_level"]
    assert concurrency_level["max_concurrency"] == 10
    assert "num_workers" in concurrency_level["default_concurrency"]


def test_budget_is_wired_into_stream_http_client():
    source, streams, api_budget = _get_api_budget()
    assert isinstance(api_budget, HttpAPIBudget)

    deals_stream = next(stream for stream in streams if stream.name == "deals")
    stream_budget = deals_stream._stream_partition_generator._partition_factory._retriever.requester._http_client._api_budget
    assert stream_budget is api_budget


@pytest.mark.parametrize(
    "config_override,expected_workers",
    [
        pytest.param({}, 3, id="default_num_workers"),
        pytest.param({"num_workers": 7}, 7, id="configured_num_workers"),
    ],
)
def test_concurrency_level_resolves_from_config(config_override, expected_workers):
    config = {**_CONFIG, **config_override}
    source = get_source(config)
    # The resolved concurrency level is the max_workers of the thread pool backing the concurrent source.
    assert source._concurrent_source._threadpool._threadpool._max_workers == expected_workers


def test_twenty_one_rapid_requests_take_at_least_two_seconds():
    _, _, api_budget = _get_api_budget()

    start = time.monotonic()
    for _ in range(20):
        prepared = requests.Request("GET", "https://api.pipedrive.com/v1/deals", params={"api_token": "t"}).prepare()
        api_budget.acquire_call(prepared)
    # The first 20 calls fill the burst window without blocking.
    assert time.monotonic() - start < 1.0

    # The 21st call blocks until the oldest call leaves the rolling 2-second window.
    api_budget.acquire_call(requests.Request("GET", "https://api.pipedrive.com/v1/deals", params={"api_token": "t"}).prepare())
    assert time.monotonic() - start >= 2.0


def test_requests_outside_pipedrive_url_base_are_not_throttled():
    _, _, api_budget = _get_api_budget()
    prepared = requests.Request("GET", "https://example.com/x").prepare()
    assert api_budget.get_matching_policy(prepared) is None
