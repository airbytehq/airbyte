#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
import tempfile
import time
from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping, Optional

import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.call_rate import (
    APIBudget,
    CallRateLimitHit,
    FixedWindowCallRatePolicy,
    HttpRequestMatcher,
    MovingWindowCallRatePolicy,
    Rate,
    UnlimitedCallRatePolicy,
)
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH
from requests import Request


class StubDummyHttpStream(HttpStream):
    url_base = "https://test_base_url.com"
    primary_key = "some_key"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return {"next_page_token": True}  # endless pages

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
    try_all_types_of_requests = pytest.mark.parametrize(
        "request_factory",
        [Request, lambda *args, **kwargs: Request(*args, **kwargs).prepare()],
    )

    @try_all_types_of_requests
    def test_url(self, request_factory):
        matcher = HttpRequestMatcher(url="http://some_url/")
        assert not matcher(request_factory(url="http://some_wrong_url"))
        assert matcher(request_factory(url="http://some_url"))

    @try_all_types_of_requests
    def test_method(self, request_factory):
        matcher = HttpRequestMatcher(method="GET")
        assert not matcher(request_factory(url="http://some_url"))
        assert not matcher(request_factory(url="http://some_url", method="POST"))
        assert matcher(request_factory(url="http://some_url", method="GET"))

    @try_all_types_of_requests
    def test_params(self, request_factory):
        matcher = HttpRequestMatcher(params={"param1": 10, "param2": 15})
        assert not matcher(request_factory(url="http://some_url/"))
        assert not matcher(request_factory(url="http://some_url/", params={"param1": 10, "param3": 100}))
        assert not matcher(request_factory(url="http://some_url/", params={"param1": 10, "param2": 10}))
        assert matcher(request_factory(url="http://some_url/", params={"param1": 10, "param2": 15, "param3": 100}))

    @try_all_types_of_requests
    def test_header(self, request_factory):
        matcher = HttpRequestMatcher(headers={"header1": 10, "header2": 15})
        assert not matcher(request_factory(url="http://some_url"))
        assert not matcher(request_factory(url="http://some_url", headers={"header1": "10", "header3": "100"}))
        assert not matcher(request_factory(url="http://some_url", headers={"header1": "10", "header2": "10"}))
        assert matcher(request_factory(url="http://some_url", headers={"header1": "10", "header2": "15", "header3": "100"}))

    @try_all_types_of_requests
    def test_combination(self, request_factory):
        matcher = HttpRequestMatcher(method="GET", url="http://some_url/", headers={"header1": 10}, params={"param2": "test"})
        assert matcher(request_factory(method="GET", url="http://some_url", headers={"header1": "10"}, params={"param2": "test"}))
        assert not matcher(request_factory(method="GET", url="http://some_url", headers={"header1": "10"}))
        assert not matcher(request_factory(method="GET", url="http://some_url"))
        assert not matcher(request_factory(url="http://some_url"))


def test_http_request_matching(mocker):
    """Test policy lookup based on matchers."""
    users_policy = mocker.Mock(spec=MovingWindowCallRatePolicy)
    groups_policy = mocker.Mock(spec=MovingWindowCallRatePolicy)
    root_policy = mocker.Mock(spec=MovingWindowCallRatePolicy)

    users_policy.matches.side_effect = HttpRequestMatcher(url="http://domain/api/users", method="GET")
    groups_policy.matches.side_effect = HttpRequestMatcher(url="http://domain/api/groups", method="POST")
    root_policy.matches.side_effect = HttpRequestMatcher(method="GET")
    api_budget = APIBudget(
        policies=[
            users_policy,
            groups_policy,
            root_policy,
        ]
    )

    api_budget.acquire_call(Request("POST", url="http://domain/unmatched_endpoint"), block=False), "unrestricted call"
    users_policy.try_acquire.assert_not_called()
    groups_policy.try_acquire.assert_not_called()
    root_policy.try_acquire.assert_not_called()

    users_request = Request("GET", url="http://domain/api/users")
    api_budget.acquire_call(users_request, block=False), "first call, first matcher"
    users_policy.try_acquire.assert_called_once_with(users_request, weight=1)
    groups_policy.try_acquire.assert_not_called()
    root_policy.try_acquire.assert_not_called()

    api_budget.acquire_call(Request("GET", url="http://domain/api/users"), block=False), "second call, first matcher"
    assert users_policy.try_acquire.call_count == 2
    groups_policy.try_acquire.assert_not_called()
    root_policy.try_acquire.assert_not_called()

    group_request = Request("POST", url="http://domain/api/groups")
    api_budget.acquire_call(group_request, block=False), "first call, second matcher"
    assert users_policy.try_acquire.call_count == 2
    groups_policy.try_acquire.assert_called_once_with(group_request, weight=1)
    root_policy.try_acquire.assert_not_called()

    api_budget.acquire_call(Request("POST", url="http://domain/api/groups"), block=False), "second call, second matcher"
    assert users_policy.try_acquire.call_count == 2
    assert groups_policy.try_acquire.call_count == 2
    root_policy.try_acquire.assert_not_called()

    any_get_request = Request("GET", url="http://domain/api/")
    api_budget.acquire_call(any_get_request, block=False), "first call, third matcher"
    assert users_policy.try_acquire.call_count == 2
    assert groups_policy.try_acquire.call_count == 2
    root_policy.try_acquire.assert_called_once_with(any_get_request, weight=1)


class TestUnlimitedCallRatePolicy:
    def test_try_acquire(self, mocker):
        policy = UnlimitedCallRatePolicy(matchers=[])
        assert policy.matches(mocker.Mock()), "should match anything"
        policy.try_acquire(mocker.Mock(), weight=1)
        policy.try_acquire(mocker.Mock(), weight=10)

    def test_update(self):
        policy = UnlimitedCallRatePolicy(matchers=[])
        policy.update(available_calls=10, call_reset_ts=datetime.now())
        policy.update(available_calls=None, call_reset_ts=datetime.now())
        policy.update(available_calls=10, call_reset_ts=None)


class TestFixedWindowCallRatePolicy:
    def test_limit_rate(self, mocker):
        policy = FixedWindowCallRatePolicy(matchers=[], next_reset_ts=datetime.now(), period=timedelta(hours=1), call_limit=100)
        policy.try_acquire(mocker.Mock(), weight=1)
        policy.try_acquire(mocker.Mock(), weight=20)
        with pytest.raises(ValueError, match="Weight can not exceed the call limit"):
            policy.try_acquire(mocker.Mock(), weight=101)

        with pytest.raises(CallRateLimitHit) as exc:
            policy.try_acquire(mocker.Mock(), weight=100 - 20 - 1 + 1)

        assert exc.value.time_to_wait
        assert exc.value.weight == 100 - 20 - 1 + 1
        assert exc.value.item

    def test_update_available_calls(self, mocker):
        policy = FixedWindowCallRatePolicy(matchers=[], next_reset_ts=datetime.now(), period=timedelta(hours=1), call_limit=100)
        # update to decrease number of calls available
        policy.update(available_calls=2, call_reset_ts=None)
        # hit the limit with weight=3
        with pytest.raises(CallRateLimitHit):
            policy.try_acquire(mocker.Mock(), weight=3)
        # ok with less weight=1
        policy.try_acquire(mocker.Mock(), weight=1)

        # update to increase number of calls available, ignored
        policy.update(available_calls=20, call_reset_ts=None)
        # so we still hit the limit with weight=3
        with pytest.raises(CallRateLimitHit):
            policy.try_acquire(mocker.Mock(), weight=3)


class TestMovingWindowCallRatePolicy:
    def test_no_rates(self):
        """should raise a ValueError when no rates provided"""
        with pytest.raises(ValueError, match="The list of rates can not be empty"):
            MovingWindowCallRatePolicy(rates=[], matchers=[])

    def test_limit_rate(self):
        """try_acquire must respect configured call rate and throw CallRateLimitHit when hit the limit."""
        policy = MovingWindowCallRatePolicy(rates=[Rate(10, timedelta(minutes=1))], matchers=[])

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
        policy = MovingWindowCallRatePolicy(rates=[Rate(10, timedelta(minutes=1))], matchers=[])

        policy.try_acquire("call", weight=2), "1st call with weight of 2"
        with pytest.raises(CallRateLimitHit) as excinfo:
            policy.try_acquire("call", weight=9), "2nd call, over limit since 2 + 9 = 11 > 10"
        assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(60, 0.1), "should wait 1 minute before next call"

    def test_multiple_limit_rates(self):
        """try_acquire must take into all call rates and apply stricter."""
        policy = MovingWindowCallRatePolicy(
            matchers=[],
            rates=[
                Rate(10, timedelta(minutes=10)),
                Rate(3, timedelta(seconds=10)),
                Rate(2, timedelta(hours=1)),
            ],
        )

        policy.try_acquire("call", weight=2), "1 call"

        with pytest.raises(CallRateLimitHit) as excinfo:
            policy.try_acquire("call", weight=1), "1 call"

        assert excinfo.value.time_to_wait.total_seconds() == pytest.approx(3600, 0.1)
        assert str(excinfo.value) == "Bucket for item=call with Rate limit=2/1.0h is already full"


class TestHttpStreamIntegration:
    def test_without_cache(self, mocker, requests_mock):
        """Test that HttpStream will use call budget when provided"""
        requests_mock.get(f"{StubDummyHttpStream.url_base}/", json={"data": "test"})

        mocker.patch.object(MovingWindowCallRatePolicy, "try_acquire")

        api_budget = APIBudget(
            policies=[
                MovingWindowCallRatePolicy(
                    matchers=[HttpRequestMatcher(url=f"{StubDummyHttpStream.url_base}/", method="GET")],
                    rates=[
                        Rate(2, timedelta(minutes=1)),
                    ],
                ),
            ]
        )

        stream = StubDummyHttpStream(api_budget=api_budget, authenticator=TokenAuthenticator(token="ABCD"))
        for i in range(10):
            records = stream.read_records(SyncMode.full_refresh)
            assert next(records) == {"data": "some_data"}

        assert MovingWindowCallRatePolicy.try_acquire.call_count == 10

    @pytest.mark.usefixtures("enable_cache")
    def test_with_cache(self, mocker, requests_mock):
        """Test that HttpStream will use call budget when provided and not cached"""
        requests_mock.get(f"{StubDummyHttpStream.url_base}/", json={"data": "test"})

        mocker.patch.object(MovingWindowCallRatePolicy, "try_acquire")

        api_budget = APIBudget(
            policies=[
                MovingWindowCallRatePolicy(
                    matchers=[
                        HttpRequestMatcher(url=f"{StubDummyHttpStream.url_base}/", method="GET"),
                    ],
                    rates=[
                        Rate(2, timedelta(minutes=1)),
                    ],
                )
            ]
        )

        stream = StubDummyCacheHttpStream(api_budget=api_budget)
        for i in range(10):
            records = stream.read_records(SyncMode.full_refresh)
            assert next(records) == {"data": "some_data"}

        assert MovingWindowCallRatePolicy.try_acquire.call_count == 1
