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


@pytest.fixture(name="enable_cache")
def enable_cache_fixture():
    prev_cache_path = os.environ.get(ENV_REQUEST_CACHE_PATH)
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ[ENV_REQUEST_CACHE_PATH] = temp_dir
        yield

    if prev_cache_path is not None:
        os.environ[ENV_REQUEST_CACHE_PATH] = prev_cache_path


def test_http_request_matchers(mocker):
    users_policy = mocker.Mock(spec=CallRatePolicy)
    groups_policy = mocker.Mock(spec=CallRatePolicy)

    api_budget = APIBudget()
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/users", method="GET"),
        policy=users_policy,
    )
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/groups", method="POST"),
        policy=groups_policy,
    )

    api_budget.acquire_call(Request("POST", url="/unmatched_endpoint"), block=False), "unrestricted call"
    users_policy.try_acquire.assert_not_called()
    groups_policy.try_acquire.assert_not_called()

    request = Request("GET", url="/users")
    api_budget.acquire_call(request, block=False), "first call"
    users_policy.try_acquire.assert_called_once_with(request)
    groups_policy.try_acquire.assert_not_called()

    api_budget.acquire_call(Request("GET", url="/users"), block=False), "second call"

    # for i in range(8):
    #     api_budget.acquire_call(Request("GET", url="/users"), block=False), f"{i + 3} call"

    # with pytest.raises(CallRateLimitHit) as excinfo:
    #     api_budget.acquire_call(Request("GET", url="/users"), block=False), "call over limit"
    # assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(60, 0.1)
    #
    # with pytest.raises(CallRateLimitHit) as excinfo:
    #     api_budget.acquire_call(Request("GET", url="/users"), block=False), "call over limit"
    # assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(60 - 5, 0.1)

    api_budget.acquire_call(Request("POST", url="/groups"), block=False), "doesn't affect other policies"
    api_budget.acquire_call(Request("POST", url="/list"), block=False), "unrestricted call"


class TestCallRatePolicy:

    def test_limit_rate(self):
        """try_acquire must respect configured call rate and throw CallRateLimitHit when hit the limit."""
        policy = CallRatePolicy(rates=[Rate(10, Duration.MINUTE)])

        for i in range(10):
            policy.try_acquire("call", weight=1), f"{i + 1} call"

        with pytest.raises(CallRateLimitHit) as excinfo1:
            policy.try_acquire("call", weight=1), "call over limit"
        assert excinfo1.value.time_to_wait.total_seconds() == pytest.approx(60, 0.1)

        time.sleep(0.5)

        with pytest.raises(CallRateLimitHit) as excinfo2:
            policy.try_acquire("call", weight=1), "call over limit"
        assert excinfo2.value.time_to_wait.total_seconds() == pytest.approx(60 - 5, 0.1)

        assert excinfo2.value.time_to_wait < excinfo1.value.time_to_wait, "time to wait must decrease over time"

    def test_limit_rate_support_custom_weight(self):
        """try_acquire must take into account provided weight and throw CallRateLimitHit when hit the limit."""
        policy = CallRatePolicy(rates=[Rate(10, Duration.MINUTE)])

        policy.try_acquire("call", weight=2), "1 call"
        with pytest.raises(CallRateLimitHit) as excinfo:
            policy.try_acquire("call", weight=9), "1 call"
        assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(60, 0.1)

    def test_multiple_limit_rates(self):
        """try_acquire must take into all call rates and apply stricter."""
        policy = CallRatePolicy(
            rates=[
                Rate(10, Duration.MINUTE),
                Rate(3, Duration.SECOND * 10),
                Rate(2, Duration.HOUR),
            ],
        )

        policy.try_acquire("call", weight=2), "1 call"

        with pytest.raises(CallRateLimitHit) as excinfo:
            policy.try_acquire("call", weight=1), "1 call"

        assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(3600, 0.1)
        assert str(excinfo.value) == 'Bucket for item=call with Rate limit=2/1.0h is already full'


class TestHttpStreamIntegration:
    def test_without_cache(self, mocker, requests_mock):
        """Test that HttpStream will use call budget when provided"""
        requests_mock.get(f"{StubDummyHttpStream.url_base}/", json={"data": "test"})

        mocker.patch.object(CallRatePolicy, "try_acquire")

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

    @pytest.mark.usefixtures("enable_cache")
    def test_with_cache(self, mocker, requests_mock):
        """Test that HttpStream will use call budget when provided and not cached"""
        requests_mock.get(f"{StubDummyHttpStream.url_base}/", json={"data": "test"})

        mocker.patch.object(CallRatePolicy, "try_acquire")

        api_budget = APIBudget()
        api_budget.add_policy(
            request_matcher=HttpRequestMatcher(url=f"{StubDummyHttpStream.url_base}/", method="GET"),
            policy=CallRatePolicy(
                rates=[
                    Rate(2, Duration.MINUTE),
                ],
            ),
        )

        stream = StubDummyCacheHttpStream(api_budget=api_budget)
        records = stream.read_records(SyncMode.full_refresh)

        for i in range(10):
            assert next(records) == {"data": "some_data"}

        assert CallRatePolicy.try_acquire.call_count == 1
