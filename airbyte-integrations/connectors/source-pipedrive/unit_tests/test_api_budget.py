#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import logging

import pytest
import requests
import requests_mock
from conftest import get_source

from airbyte_cdk.models import Status
from airbyte_cdk.sources.streams.call_rate import CallRateLimitHit, HttpAPIBudget, MovingWindowCallRatePolicy


_CONFIG = {"api_token": "t", "replication_start_date": "2024-01-01T00:00:00Z"}


def _get_api_budget(config=_CONFIG):
    source = get_source(config)
    # The constructor's api budget is only populated once streams are built.
    source.streams(config)
    return source._constructor._api_budget


def _prepared(url):
    return requests.Request("GET", url, params={"api_token": "t"}).prepare()


def test_every_request_goes_through_the_budget(mocker):
    acquire = mocker.spy(MovingWindowCallRatePolicy, "try_acquire")
    with requests_mock.Mocker() as http:
        http.get("https://api.pipedrive.com/api/v1/currencies", complete_qs=False, json={"success": True, "data": [{"id": 1, "code": "USD"}]})
        status = get_source(_CONFIG).check(logging.getLogger("airbyte"), _CONFIG)

    assert status.status == Status.SUCCEEDED
    assert acquire.call_count == 1
    assert acquire.call_args.args[1].url.startswith("https://api.pipedrive.com/api/v1/currencies")


@pytest.mark.parametrize(
    "config_override,expected_workers",
    [
        pytest.param({}, 3, id="default_num_workers"),
        pytest.param({"num_workers": 7}, 7, id="configured_num_workers"),
        pytest.param({"num_workers": 50}, 10, id="clamped_to_max_concurrency"),
        pytest.param({"num_workers": None}, 3, id="null_falls_back_to_default"),
    ],
)
def test_concurrency_level_resolves_from_config(config_override, expected_workers):
    config = {**_CONFIG, **config_override}
    source = get_source(config)
    # The resolved concurrency level is the max_workers of the thread pool backing the concurrent source.
    assert source._concurrent_source._threadpool._threadpool._max_workers == expected_workers


def test_twenty_first_call_in_the_window_is_blocked():
    api_budget = _get_api_budget()
    assert isinstance(api_budget, HttpAPIBudget)

    for _ in range(20):
        api_budget.acquire_call(_prepared("https://api.pipedrive.com/api/v1/deals"), block=False)

    with pytest.raises(CallRateLimitHit) as limit_hit:
        api_budget.acquire_call(_prepared("https://api.pipedrive.com/api/v1/deals"), block=False)
    assert 0 < limit_hit.value.time_to_wait.total_seconds() <= 2


@pytest.mark.parametrize(
    "url",
    [
        "https://api.pipedrive.com/api/v1/deals",
        "https://api.pipedrive.com/api/v2/deals",
        "https://acme.pipedrive.com/api/v1/deals",
    ],
)
def test_pipedrive_hosts_and_api_versions_are_throttled(url):
    assert _get_api_budget().get_matching_policy(_prepared(url)) is not None


def test_requests_outside_pipedrive_are_not_throttled():
    assert _get_api_budget().get_matching_policy(requests.Request("GET", "https://example.com/x").prepare()) is None


def test_rate_limit_response_does_not_break_the_budget():
    api_budget = _get_api_budget()
    request = _prepared("https://api.pipedrive.com/api/v1/deals")
    response = requests.Response()
    response.status_code = 429
    response.headers["x-ratelimit-remaining"] = "0"

    api_budget.update_from_response(request, response)

    # The policy stays usable: the moving window, not the header, is what throttles.
    api_budget.acquire_call(request, block=False)
