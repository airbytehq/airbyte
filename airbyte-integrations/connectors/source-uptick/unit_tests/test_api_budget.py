# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards the shared `api_budget`, `concurrency_level`, and `Retry-After` wait cap in
`manifest.yaml`: a single global moving-window budget driven by `max_requests_per_minute`
(default 60 calls per minute), `num_workers` wiring into the resolved concurrency level, and
a `Retry-After` at the 1800s cap that stops the stream instead of waiting.
"""

import json
from datetime import timedelta

import pytest
from conftest import base_config, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ConcurrencyLevel as ConcurrencyLevelModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import Rate as RateModel
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_BASE_URL = "https://demo.onuptick.com"
_STREAM_NAME = "task_profitability"
_TOKEN_REQUEST_BODY = "grant_type=password&client_id=client-id&client_secret=client-secret&username=user%40example.com&password=password"


def _service_group_page(record_id: int, next_url: str | None) -> HttpResponse:
    record = {
        "type": "ServiceGroup",
        "id": record_id,
        "attributes": {"created": "2026-01-01T00:00:00.000000+0000", "updated": "2026-01-02T00:00:00.000000+0000", "name": "g"},
    }
    return HttpResponse(body=json.dumps({"data": [record], "links": {"next": next_url}}), status_code=200)


@pytest.mark.parametrize(
    "config_override,expected_limit",
    [
        pytest.param({}, 60, id="default_max_requests_per_minute"),
        pytest.param({"max_requests_per_minute": 120}, 120, id="configured_max_requests_per_minute"),
    ],
)
def test_budget_policy_resolves_limit_from_config(config_override, expected_limit) -> None:
    config = base_config(**config_override)
    source = get_source(config)

    api_budget = source.resolved_manifest["api_budget"]
    policies = api_budget["policies"]
    # One global MovingWindowCallRatePolicy: N calls per 60s window, empty matchers so every
    # request on every stream counts against the same budget.
    assert len(policies) == 1
    assert policies[0]["matchers"] == []
    # The rates entry carries no `type` discriminator, so inject it for create_component.
    rate = source._constructor.create_component(RateModel, {**policies[0]["rates"][0], "type": "Rate"}, source._config)
    assert rate.limit == expected_limit
    assert rate.interval == timedelta(minutes=1)


@pytest.mark.parametrize(
    "config_override,expected_workers",
    [
        pytest.param({}, 3, id="default_num_workers"),
        pytest.param({"num_workers": 7}, 7, id="configured_num_workers"),
        pytest.param({"num_workers": 50}, 10, id="clamped_to_max_concurrency"),
    ],
)
def test_concurrency_level_resolves_from_config(config_override, expected_workers) -> None:
    config = base_config(**config_override)
    source = get_source(config)
    component = source._constructor.create_component(ConcurrencyLevelModel, source.resolved_manifest["concurrency_level"], source._config)

    assert component.get_concurrency_level() == expected_workers


def test_global_budget_throttles_past_60_calls_per_minute(virtual_clock: list[float]) -> None:
    """61 pages of one stream must fit under the 60/min budget: the 61st acquire waits for the
    first window slot to expire instead of raising CallRateLimitHit."""
    page_request = HttpRequest(f"{_BASE_URL}/api/v2.15/servicegroups/", query_params=ANY_QUERY_PARAMS)
    pages = [
        _service_group_page(page_number, f"{_BASE_URL}/api/v2.15/servicegroups/?page={page_number + 1}" if page_number < 61 else None)
        for page_number in range(1, 62)
    ]

    config = base_config()
    catalog = CatalogBuilder().with_stream("servicegroups", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(f"{_BASE_URL}/api/oauth2/token/", body=_TOKEN_REQUEST_BODY),
            HttpResponse('{"access_token": "token", "expires_in": 3600}', 200),
        )
        http_mocker.get(page_request, pages)
        output = read(get_source(config, catalog), config, catalog)

    assert [message.record.data["id"] for message in output.records] == list(range(1, 62))
    assert output.errors == []
    http_mocker.assert_number_of_calls(page_request, 61)
    # The budget blocks once 60 calls sit inside the 60s window; the observed cool-down is ~60s
    # while the oldest call slides out of the moving window.
    assert virtual_clock and sum(virtual_clock) >= 59, f"expected a ~60s budget wait for call 61, got {virtual_clock}"


def test_higher_configured_limit_does_not_wait_for_61_calls(virtual_clock: list[float]) -> None:
    """With `max_requests_per_minute` raised to 120, the same 61-page read fits inside one
    window: every page is served without a budget wait."""
    page_request = HttpRequest(f"{_BASE_URL}/api/v2.15/servicegroups/", query_params=ANY_QUERY_PARAMS)
    pages = [
        _service_group_page(page_number, f"{_BASE_URL}/api/v2.15/servicegroups/?page={page_number + 1}" if page_number < 61 else None)
        for page_number in range(1, 62)
    ]

    config = base_config(max_requests_per_minute=120)
    catalog = CatalogBuilder().with_stream("servicegroups", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(f"{_BASE_URL}/api/oauth2/token/", body=_TOKEN_REQUEST_BODY),
            HttpResponse('{"access_token": "token", "expires_in": 3600}', 200),
        )
        http_mocker.get(page_request, pages)
        output = read(get_source(config, catalog), config, catalog)

    assert [message.record.data["id"] for message in output.records] == list(range(1, 62))
    assert output.errors == []
    http_mocker.assert_number_of_calls(page_request, 61)
    assert virtual_clock == []


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
