#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
import tempfile
import time
from typing import Iterable, Mapping

import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.call_rate import APIBudget, CallRateLimitHit, CallRatePolicy, Duration, HttpRequestMatcher, Rate
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH
from requests import Request


class StubDummyHttpStream(HttpStream):
    url_base = "https://test_base_url.com"
    primary_key = "some_key"

    def next_page_token(self, *args, **kwargs):
        return True  # endless pages

    def path(self, **kwargs) -> str:
        return ""

    def parse_response(self, *args, **kwargs) -> Iterable[Mapping]:
        yield {"data": "some_data"}


class StubDummyCacheHttpStream(StubDummyHttpStream):
    use_cache = True


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


def test_order_of_rates():
    """CallRatePolicy will check all rates and apply stricter."""
    api_budget = APIBudget()
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/users", method="GET"),
        policy=CallRatePolicy(
            rates=[
                Rate(5, Duration.MINUTE),
                Rate(2, Duration.HOUR),
            ],
        ),
    )

    for i in range(2):
        api_budget.acquire_call(Request("GET", url="/users"), block=False), f"{i + 3} call"

    with pytest.raises(CallRateLimitHit) as excinfo:
        api_budget.acquire_call(Request("GET", url="/users"), block=False), "call over hour limit"
    assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(60 * 60, 0.1)


def test_http_stream_integration(mocker):
    """Test that HttpStream will use call budget when provided"""
    response = requests.Response()
    response.status_code = 200

    mocker.patch.object(CallRatePolicy, "try_acquire")
    mocker.patch.object(requests.Session, "send", return_value=response)

    api_budget = APIBudget()
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url=f"{StubDummyHttpStream.url_base}/", method="GET"),
        policy=CallRatePolicy(
            rates=[
                Rate(2, Duration.MINUTE),
            ],
        ),
    )

    stream = StubDummyHttpStream(api_budget=api_budget)
    records = stream.read_records(SyncMode.full_refresh)
    for i in range(10):
        assert next(records) == {"data": "some_data"}

    assert CallRatePolicy.try_acquire.call_count == 10


def test_http_stream_with_cache_integration(mocker):
    """Test that HttpStream will use call budget when provided and not cached"""
    response = requests.Response()
    response.status_code = 200
    response.request = requests.PreparedRequest()

    mocker.patch.object(CallRatePolicy, "try_acquire")
    mocker.patch.object(requests.Session, "send", return_value=response)

    api_budget = APIBudget()
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url=f"{StubDummyHttpStream.url_base}/", method="GET"),
        policy=CallRatePolicy(
            rates=[
                Rate(2, Duration.MINUTE),
            ],
        ),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ[ENV_REQUEST_CACHE_PATH] = temp_dir

        stream = StubDummyCacheHttpStream(api_budget=api_budget)
        records = stream.read_records(SyncMode.full_refresh)
        for i in range(10):
            assert next(records) == {"data": "some_data"}

    assert CallRatePolicy.try_acquire.call_count == 10
