# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import timedelta

import pytest
import requests
import yaml
from _helpers import CONFIG
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.sources.streams.call_rate import CallRateLimitHit, HttpAPIBudget, MovingWindowCallRatePolicy


def budget() -> HttpAPIBudget:
    source = get_source(CONFIG)
    source.streams(CONFIG)
    return source._constructor._api_budget


def prepared(path: str = "users/me") -> requests.PreparedRequest:
    return requests.Request("GET", f"https://api.calendly.com/{path}").prepare()


def test_budget_is_one_500_per_minute_moving_window_policy() -> None:
    actual = budget()
    assert isinstance(actual, HttpAPIBudget)
    definition = yaml.safe_load(_YAML_FILE_PATH.read_text())["api_budget"]
    assert definition["ratelimit_remaining_header"] == "X-RateLimit-Remaining"
    assert definition.get("ratelimit_reset_header", "ratelimit-reset") == "ratelimit-reset"
    assert definition["status_codes_for_ratelimit_hit"] == [429]
    assert len(definition["policies"]) == 1
    assert definition["policies"][0]["rates"] == [{"limit": 500, "interval": "PT1M"}]
    policy = actual.get_matching_policy(prepared())
    assert isinstance(policy, MovingWindowCallRatePolicy)
    for path in ["users/me", "event_types", "groups", "organization_memberships", "scheduled_events", "scheduled_events/event/invitees"]:
        assert actual.get_matching_policy(prepared(path)) is policy
    assert actual.get_matching_policy(requests.Request("GET", "https://example.com/users/me").prepare()) is None


def test_five_hundred_and_first_call_is_blocked() -> None:
    actual = budget()
    for _ in range(500):
        actual.acquire_call(prepared(), block=False)
    with pytest.raises(CallRateLimitHit) as error:
        actual.acquire_call(prepared(), block=False)
    assert timedelta(0) < error.value.time_to_wait <= timedelta(minutes=1)


@pytest.mark.parametrize("remaining", ["0", "1", "499"])
def test_remaining_header_updates_the_budget(remaining: str) -> None:
    actual = budget()
    response = requests.Response()
    response.status_code = 200
    response.headers.update({"X-RateLimit-Remaining": remaining, "X-RateLimit-Reset": "60"})
    actual.update_from_response(prepared(), response)
    if remaining == "0":
        with pytest.raises(CallRateLimitHit) as error:
            actual.acquire_call(prepared(), block=False)
        assert timedelta(0) < error.value.time_to_wait <= timedelta(minutes=1)
    else:
        actual.acquire_call(prepared(), block=False)


def test_concurrency_defaults_to_four_with_maximum_ten() -> None:
    definition = yaml.safe_load(_YAML_FILE_PATH.read_text())["concurrency_level"]
    assert definition == {"type": "ConcurrencyLevel", "default_concurrency": 4, "max_concurrency": 10}
    assert get_source(CONFIG)._concurrent_source._threadpool._threadpool._max_workers == 4
