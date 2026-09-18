# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards the shared `api_budget`, `concurrency_level`, and `Retry-After` wait cap in
`manifest.yaml`: a single global moving-window budget, `num_workers` wiring into the
concurrent source thread pool, and a `Retry-After` at the 1800s cap that stops the
stream instead of waiting.
"""

import pytest
import requests
from conftest import base_config, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.call_rate import CallRateLimitHit, HttpAPIBudget, MovingWindowCallRatePolicy
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_BASE_URL = "https://demo.onuptick.com"
_STREAM_NAME = "task_profitability"
_TOKEN_REQUEST_BODY = "grant_type=password&client_id=client-id&client_secret=client-secret&username=user%40example.com&password=password"


def _get_api_budget(config=None):
    config = config or base_config()
    source = get_source(config)
    # The constructor's api budget is only populated once streams are built.
    source.streams(config)
    return source._constructor._api_budget


def _prepared(url):
    return requests.Request("GET", url).prepare()


def test_budget_policy_is_a_60_per_minute_moving_window():
    api_budget = _get_api_budget()
    assert isinstance(api_budget, HttpAPIBudget)

    policies = api_budget._policies
    assert len(policies) == 1
    assert isinstance(policies[0], MovingWindowCallRatePolicy)

    # Matchers are empty, so every request is throttled by the single global budget.
    assert api_budget.get_matching_policy(_prepared(f"{_BASE_URL}/api/v2.15/tasks/")) is not None
    assert api_budget.get_matching_policy(_prepared("https://example.com/x")) is not None


def test_sixty_first_call_in_the_window_is_blocked():
    api_budget = _get_api_budget()
    for _ in range(60):
        api_budget.acquire_call(_prepared(f"{_BASE_URL}/api/v2.15/tasks/"), block=False)

    with pytest.raises(CallRateLimitHit) as limit_hit:
        api_budget.acquire_call(_prepared(f"{_BASE_URL}/api/v2.15/tasks/"), block=False)
    assert 0 < limit_hit.value.time_to_wait.total_seconds() <= 60


@pytest.mark.parametrize(
    "config_override,expected_workers",
    [
        pytest.param({}, 3, id="default_num_workers"),
        pytest.param({"num_workers": 7}, 7, id="configured_num_workers"),
        pytest.param({"num_workers": 10}, 10, id="max_num_workers"),
        pytest.param({"num_workers": 50}, 10, id="clamped_to_max_concurrency"),
        pytest.param({"num_workers": 0}, 3, id="zero_falls_back_to_default"),
        pytest.param({"num_workers": None}, 3, id="null_falls_back_to_default"),
        pytest.param({"num_workers": True}, 3, id="boolean_falls_back_to_default"),
    ],
)
def test_concurrency_level_resolves_from_config(config_override, expected_workers):
    config = base_config(**config_override)
    source = get_source(config)
    # The resolved concurrency level is the max_workers of the thread pool backing the concurrent source.
    assert source._concurrent_source._threadpool._threadpool._max_workers == expected_workers


def test_retry_after_at_cap_terminates_instead_of_waiting(monkeypatch) -> None:
    sleeps = []
    monkeypatch.setattr("time.sleep", lambda duration: sleeps.append(duration))

    config = base_config()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        token_request = HttpRequest(f"{_BASE_URL}/api/oauth2/token/", body=_TOKEN_REQUEST_BODY)
        stream_request = HttpRequest(f"{_BASE_URL}/api/v2/intelligencereports/profitability_by_task/", query_params=ANY_QUERY_PARAMS)
        http_mocker.post(token_request, HttpResponse('{"access_token": "token", "expires_in": 3600}', 200))
        http_mocker.get(stream_request, HttpResponse('{"detail": "throttled"}', 429, headers={"Retry-After": "1800"}))
        output = read(get_source(config, catalog), config, catalog)

    assert len(output.records) == 0
    stream_errors = [
        error.trace.error
        for error in output.errors
        if error.trace.error.failure_type == FailureType.transient_error and "rate limit wait time" in error.trace.error.message
    ]
    assert len(stream_errors) == 1, f"expected exactly one transient rate-limit error, got {output.errors}"
    assert all(duration < 1800 for duration in sleeps), f"a wait at or above the 1800s cap was taken: {sleeps}"
