#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
import tempfile
import time
from typing import Iterable, Mapping

import pytest

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


class TestHttpRequestMatcher:
    def test_url(self):
        matcher = HttpRequestMatcher(url="some_url")
        assert not matcher(Request())
        assert not matcher(Request(url="wrong"))
        assert matcher(Request(url="some_url"))

    def test_method(self):
        matcher = HttpRequestMatcher(method="GET")
        assert not matcher(Request())
        assert not matcher(Request(method="POST"))
        assert matcher(Request(method="GET"))

    def test_params(self):
        matcher = HttpRequestMatcher(params={"param1": 10, "param2": 15})
        assert not matcher(Request(url="some_url"))
        assert not matcher(Request(params={"param1": 10, "param3": 100}))
        assert not matcher(Request(params={"param1": 10, "param2": 10}))
        assert matcher(Request(params={"param1": 10, "param2": 15, "param3": 100}))

    def test_header(self):
        matcher = HttpRequestMatcher(headers={"header1": 10, "header2": 15})
        assert not matcher(Request(url="some_url"))
        assert not matcher(Request(headers={"header1": 10, "header3": 100}))
        assert not matcher(Request(headers={"header1": 10, "header2": 10}))
        assert matcher(Request(headers={"header1": 10, "header2": 15, "header3": 100}))

    def test_combination(self):
        matcher = HttpRequestMatcher(method="GET", url="some_url", headers={"header1": 10}, params={"param2": "test"})
        assert matcher(Request(method="GET", url="some_url", headers={"header1": 10}, params={"param2": "test"}))
        assert not matcher(Request(method="GET", url="some_url", headers={"header1": 10}, ))
        assert not matcher(Request(method="GET", url="some_url", ))
        assert not matcher(Request(method="GET", ))


def test_http_request_matching(mocker):
    """Test policy lookup based on matchers."""
    users_policy = mocker.Mock(spec=CallRatePolicy)
    groups_policy = mocker.Mock(spec=CallRatePolicy)
    root_policy = mocker.Mock(spec=CallRatePolicy)

    api_budget = APIBudget()
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/api/users", method="GET"),
        policy=users_policy,
    )
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/api/groups", method="POST"),
        policy=groups_policy,
    )
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(method="GET"),
        policy=root_policy,
    )

    api_budget.acquire_call(Request("POST", url="/unmatched_endpoint"), block=False), "unrestricted call"
    users_policy.try_acquire.assert_not_called()
    groups_policy.try_acquire.assert_not_called()
    root_policy.try_acquire.assert_not_called()

    users_request = Request("GET", url="/api/users")
    api_budget.acquire_call(users_request, block=False), "first call, first matcher"
    users_policy.try_acquire.assert_called_once_with(users_request)
    groups_policy.try_acquire.assert_not_called()
    root_policy.try_acquire.assert_not_called()

    api_budget.acquire_call(Request("GET", url="/api/users"), block=False), "second call, first matcher"
    assert users_policy.try_acquire.call_count == 2
    groups_policy.try_acquire.assert_not_called()
    root_policy.try_acquire.assert_not_called()

    group_request = Request("POST", url="/api/groups")
    api_budget.acquire_call(group_request, block=False), "first call, second matcher"
    assert users_policy.try_acquire.call_count == 2
    groups_policy.try_acquire.assert_called_once_with(group_request)
    root_policy.try_acquire.assert_not_called()

    api_budget.acquire_call(Request("POST", url="/api/groups"), block=False), "second call, second matcher"
    assert users_policy.try_acquire.call_count == 2
    assert groups_policy.try_acquire.call_count == 2
    root_policy.try_acquire.assert_not_called()

    any_get_request = Request("GET", url="/api/")
    api_budget.acquire_call(any_get_request, block=False), "first call, third matcher"
    assert users_policy.try_acquire.call_count == 2
    assert groups_policy.try_acquire.call_count == 2
    root_policy.try_acquire.assert_called_once_with(any_get_request)


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
        assert excinfo2.value.time_to_wait < excinfo1.value.time_to_wait, "time to wait must decrease over time"

    def test_limit_rate_support_custom_weight(self):
        """try_acquire must take into account provided weight and throw CallRateLimitHit when hit the limit."""
        policy = CallRatePolicy(rates=[Rate(10, Duration.MINUTE)])

        policy.try_acquire("call", weight=2), "1st call with weight of 2"
        with pytest.raises(CallRateLimitHit) as excinfo:
            policy.try_acquire("call", weight=9), "2nd call, over limit since 2 + 9 = 11 > 10"
        assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(60, 0.1), "should wait 1 minute before next call"

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
