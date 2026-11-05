# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import yaml
from freezegun import freeze_time

from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.call_rate import CallRateLimitHit, HttpAPIBudget
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.helpers import BASE, CONFIG, NOW, error, fixture_record, list_request, page, run


@pytest.mark.parametrize(
    "status,headers,wait",
    [
        (429, {"Retry-After": "7"}, 8),
        (429, {"X-Retry-After": "13"}, 14),
        (429, {"Retry-After": "7", "X-Retry-After": "121"}, 8),
        (429, {}, 11),
        (500, {}, 11),
    ],
)
@freeze_time(NOW)
def test_retryable_response_recovers(status: int, headers: dict[str, str], wait: int) -> None:
    with patch("time.sleep") as sleep, patch("airbyte_cdk.sources.streams.call_rate.APIBudget.acquire_call"), HttpMocker() as mocker:
        request = list_request("tags")
        record = fixture_record("tags")
        mocker.get(request, [error(status, headers=headers), page([record])])
        output = run("tags")
        mocker.assert_number_of_calls(request, 2)
        # The CDK adds one second to user-defined waits and also calls sleep(0).
        assert [call.args[0] for call in sleep.call_args_list if call.args[0] > 0] == [wait]
    assert output.errors == []
    assert [message.record.data for message in output.records] == [record]


@freeze_time(NOW)
def test_excessive_x_retry_after_fails_without_retrying() -> None:
    with patch("time.sleep") as sleep, patch("airbyte_cdk.sources.streams.call_rate.APIBudget.acquire_call"), HttpMocker() as mocker:
        request = list_request("tags")
        mocker.get(request, error(429, headers={"X-Retry-After": "121"}))
        output = run("tags", expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
        assert not [call for call in sleep.call_args_list if call.args[0] > 0]
    assert output.records == []
    assert output.errors


@pytest.mark.parametrize("status", [429, 500])
@freeze_time(NOW)
def test_retry_limit_is_enforced(status: int) -> None:
    with patch("time.sleep") as sleep, patch("airbyte_cdk.sources.streams.call_rate.APIBudget.acquire_call"), HttpMocker() as mocker:
        request = list_request("tags")
        mocker.get(request, error(status))
        output = run("tags", expecting_exception=True)
        mocker.assert_number_of_calls(request, 6)
        assert [call.args[0] for call in sleep.call_args_list if call.args[0] > 0] == [11, 21, 41, 81, 161]
    assert output.records == []
    assert output.errors


@pytest.mark.parametrize("region,base", [("us", BASE), ("eu", "https://api.eu.usepylon.com")])
@freeze_time(NOW)
def test_http_response_updates_the_live_budget(region: str, base: str) -> None:
    record = fixture_record("tags")
    with (
        patch.object(HttpAPIBudget, "update_from_response", autospec=True, side_effect=HttpAPIBudget.update_from_response) as update,
        HttpMocker() as mocker,
    ):
        request = list_request("tags", base=base)
        response = HttpResponse(json.dumps({"data": [record]}), headers={"X-Rate-Limit-Remaining": "0"})
        mocker.get(request, response)
        output = run("tags", cfg={**CONFIG, "region": region})
        mocker.assert_number_of_calls(request, 1)
        update.assert_called_once()
        live_budget, prepared_request, received_response = update.call_args.args
        assert received_response.headers["X-Rate-Limit-Remaining"] == "0"
        with pytest.raises(CallRateLimitHit):
            live_budget.acquire_call(prepared_request, block=False)
        live_budget.acquire_call(requests.Request("GET", base + "/teams"), block=False)
    assert output.errors == []
    assert [message.record.data for message in output.records] == [record]


ENDPOINTS = [
    ("GET", "/activity-types", 30),
    ("GET", "/issue-statuses", 30),
    ("POST", "/issues/search", 120),
    ("GET", "/issues/synthetic-id/messages", 120),
    ("GET", "/issues/synthetic-id/threads", 120),
    ("GET", "/knowledge-bases/synthetic-id/articles", 120),
    ("GET", "/accounts", 300),
    ("GET", "/contacts", 300),
    ("GET", "/tags", 300),
    ("GET", "/teams", 300),
    ("GET", "/users", 300),
    ("GET", "/custom-fields", 300),
    ("GET", "/knowledge-bases", 300),
    ("GET", "/ticket-forms", 300),
    ("GET", "/user-roles", 300),
]


@pytest.fixture
def budget(manifest_path: Path) -> HttpAPIBudget:
    manifest = yaml.safe_load(manifest_path.read_text())
    return ModelToComponentFactory().create_component(
        model_type=models.HTTPAPIBudget, component_definition=manifest["api_budget"], config={}
    )


@pytest.mark.parametrize("method,path,limit", ENDPOINTS)
@pytest.mark.parametrize("base", [BASE, "https://api.eu.usepylon.com"])
def test_budget_semantics(budget: HttpAPIBudget, method: str, path: str, limit: int, base: str) -> None:
    with freeze_time(NOW) as clock:
        request = requests.Request(method, base + path)
        other_request = requests.Request("GET", base + ("/contacts" if path == "/accounts" else "/accounts"))
        policy = budget.get_matching_policy(request)
        assert policy is not None
        assert budget.get_matching_policy(other_request) is not policy
        budget.acquire_call(request, block=False)
        clock.tick(30)
        for _ in range(limit - 1):
            budget.acquire_call(request, block=False)
        with pytest.raises(CallRateLimitHit):
            budget.acquire_call(request, block=False)
        budget.acquire_call(other_request, block=False)
        clock.tick(31)
        budget.acquire_call(request, block=False)
        with pytest.raises(CallRateLimitHit):
            budget.acquire_call(request, block=False)
        clock.tick(30)
        for _ in range(limit - 1):
            budget.acquire_call(request, block=False)
        with pytest.raises(CallRateLimitHit):
            budget.acquire_call(request, block=False)


@pytest.mark.parametrize("status,headers", [(200, {"X-Rate-Limit-Remaining": "0"}), (429, {})])
@freeze_time(NOW)
def test_response_exhausts_only_its_endpoint_budget(budget: HttpAPIBudget, status: int, headers: dict[str, str]) -> None:
    request = requests.Request("GET", BASE + "/tags")
    response = requests.Response()
    response.status_code = status
    response.headers.update(headers)
    budget.acquire_call(request, block=False)
    budget.update_from_response(request, response)
    with pytest.raises(CallRateLimitHit):
        budget.acquire_call(request, block=False)
    budget.acquire_call(requests.Request("GET", BASE + "/teams"), block=False)


def test_empty_response_does_not_exhaust_budget(budget: HttpAPIBudget) -> None:
    request = requests.Request("GET", BASE + "/tags")
    response = requests.Response()
    response.status_code = 200
    budget.update_from_response(request, response)
    budget.acquire_call(request, block=False)


@pytest.mark.parametrize("method,path,limit", ENDPOINTS)
@pytest.mark.parametrize("base", [BASE, "https://api.eu.usepylon.com"])
def test_matchers_are_endpoint_scoped(budget: HttpAPIBudget, method: str, path: str, limit: int, base: str) -> None:
    assert len(budget._policies) == len(ENDPOINTS)
    request = requests.Request(method, base + path + "?limit=999")
    policy = budget.get_matching_policy(request)
    assert policy is not None
    assert sum(candidate.matches(request) for candidate in budget._policies) == 1
    assert budget.get_matching_policy(requests.Request("DELETE", BASE + path)) is None
    assert budget.get_matching_policy(requests.Request(method, BASE + path + "/extra")) is None
    assert budget.get_matching_policy(requests.Request(method, BASE + "/prefix" + path)) is None
    if "synthetic-id" in path:
        assert budget.get_matching_policy(requests.Request(method, BASE + path.replace("synthetic-id", "another-id"))) is policy


@pytest.mark.parametrize("workers,expected", [(None, 3), (1, 1), (7, 7), (20, 10)])
def test_concurrency_defaults_and_cap(manifest_path: Path, workers: int | None, expected: int) -> None:
    manifest = yaml.safe_load(manifest_path.read_text())
    component = ModelToComponentFactory().create_component(
        model_type=models.ConcurrencyLevel,
        component_definition=manifest["concurrency_level"],
        config={} if workers is None else {"num_workers": workers},
    )
    assert component.get_concurrency_level() == expected
