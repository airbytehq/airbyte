#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import timedelta
from unittest.mock import patch

import pytest
import requests
from freezegun import freeze_time
from source_github import SourceGithub
from source_github.streams import Organizations
from source_github.utils import read_full_refresh, rotate_authenticator_token

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth.rate_limited_multiple_token import (
    RateLimitedMultipleTokenAuthenticator,
)
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now


def _source_and_authenticator(tokens: str, **config_overrides):
    """Build a source and the shared authenticator its manifest streams use."""
    config = {"access_token": tokens, "repositories": ["org/repo"], **config_overrides}
    source = SourceGithub(catalog=None, config=config, state=None)
    return source, source._get_authenticator(config)


def _remaining(authenticator, token, quota="rest"):
    return authenticator._states[token][quota].remaining


def _prepared_request(url="https://api.github.com/orgs/org1"):
    return requests.Request("GET", url).prepare()


def test_multiple_tokens(rate_limit_mock_response):
    _, authenticator = _source_and_authenticator("token_1, token_2, token_3")
    assert isinstance(authenticator, RateLimitedMultipleTokenAuthenticator)
    assert ["token_1", "token_2", "token_3"] == list(authenticator._tokens)


def test_authenticator_instance_is_shared_with_manifest_streams(rate_limit_mock_response, requests_mock):
    """The Python streams must charge the same quota counters as the declarative streams.

    Two authenticators over one set of tokens would each believe they own the full 5000-point
    budget, so the connector would plan for twice the quota GitHub actually grants. The CDK
    factory caches `RateLimitedMultipleTokenAuthenticator` by resolved constructor arguments,
    which is what makes a single instance possible — this test is what keeps it that way.
    """
    config = {"access_token": "token1,token2", "repositories": ["org/repo"], "api_url": "https://api.github.com"}
    source = SourceGithub(catalog=None, config=config, state=None)

    manifest_stream = ConcurrentDeclarativeSource.streams(source, config)[0]
    manifest_authenticator = manifest_stream._stream_partition_generator._partition_factory._retriever.requester.authenticator

    requests_mock.get("https://api.github.com/repos/org/repo", json={"full_name": "org/repo", "organization": {"login": "org"}})
    python_streams = source.streams(config)

    assert all(stream._http_client._session.auth is manifest_authenticator for stream in python_streams)
    assert len(source._constructor._rate_limited_authenticators) == 1


def test_quota_is_charged_once_across_repository_resolution_and_python_streams(rate_limit_mock_response, requests_mock):
    """Requests made while resolving repositories (manifest components) and requests made by a
    Python stream draw down one counter, not two."""
    config = {"access_token": "token1", "repositories": ["org/repo"], "api_url": "https://api.github.com"}
    source = SourceGithub(catalog=None, config=config, state=None)
    requests_mock.get("https://api.github.com/repos/org/repo", json={"full_name": "org/repo", "organization": {"login": "org"}})
    requests_mock.get("https://api.github.com/orgs/org", json={"id": 1})

    python_streams = source.streams(config)
    authenticator = source._get_authenticator(config)
    after_resolution = _remaining(authenticator, "token1")

    organizations = next(stream for stream in python_streams if isinstance(stream, Organizations))
    list(read_full_refresh(organizations))

    assert after_resolution < 5000, "repository resolution should have charged the shared counter"
    assert _remaining(authenticator, "token1") == after_resolution - 1


def test_authenticator_counter(rate_limit_mock_response, requests_mock):
    """The rate limiter reads the available limits from the GitHub API and counts requests."""
    _, authenticator = _source_and_authenticator("token1,token2,token3")

    stream = Organizations(organizations=["org1", "org2"], authenticator=authenticator)
    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    requests_mock.get("https://api.github.com/orgs/org2", json={"id": 2})
    list(read_full_refresh(stream))

    assert [(_remaining(authenticator, t), _remaining(authenticator, t, "graphql")) for t in authenticator._tokens] == [
        (4998, 5000),
        (5000, 5000),
        (5000, 5000),
    ]


def test_quota_is_seeded_lazily_and_only_once_per_token(requests_mock):
    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    rate_limit_mock = requests_mock.get(
        "https://api.github.com/rate_limit",
        json={
            "resources": {
                "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
                "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
            }
        },
    )

    _, authenticator = _source_and_authenticator("token1,token2")
    assert rate_limit_mock.call_count == 0, "counters should be seeded on first use, not at construction"

    stream = Organizations(organizations=["org1"], authenticator=authenticator)
    list(read_full_refresh(stream))
    assert rate_limit_mock.call_count == 2  # one per token, not one per authenticator per token


def test_graphql_requests_are_charged_to_the_graphql_quota(rate_limit_mock_response):
    _, authenticator = _source_and_authenticator("token1")

    authenticator(_prepared_request("https://api.github.com/graphql"))

    assert _remaining(authenticator, "token1", "graphql") == 4999
    assert _remaining(authenticator, "token1", "rest") == 5000


@patch("time.sleep")
def test_all_tokens_exhausted_raises_transient_error(sleep_mock, requests_mock):
    """The limiter rotates through every token and then fails as a transient error once the
    next reset is further away than `max_wait_time`."""
    requests_mock.get(
        "https://api.github.com/rate_limit",
        json={
            "resources": {
                "core": {"limit": 500, "used": 0, "remaining": 500, "reset": 4070908800},
                "graphql": {"limit": 500, "used": 0, "remaining": 500, "reset": 4070908800},
            }
        },
    )
    _, authenticator = _source_and_authenticator("token1,token2,token3")
    stream = Organizations(organizations=["org1"], authenticator=authenticator)

    counter_orgs = 0

    def request_callback_orgs(request, context):
        nonlocal counter_orgs
        while counter_orgs < 1_501:
            counter_orgs += 1
            context.headers = {"Link": '<https://api.github.com/orgs/org1?page=2>; rel="next"', "Content-Type": "application/json"}
            context.status_code = 200
            return json.dumps({"id": 1})

    requests_mock.get("https://api.github.com/orgs/org1", text=request_callback_orgs)

    with pytest.raises(AirbyteTracedException) as e:
        list(read_full_refresh(stream))

    assert [_remaining(authenticator, t) for t in authenticator._tokens] == [0, 0, 0]
    assert e.value.failure_type == FailureType.transient_error
    assert "Rate limit is exceeded for all provided tokens." in e.value.message


@freeze_time("2021-01-01 12:00:00")
@patch("time.sleep")
def test_exhaustion_waits_for_reset_then_refreshes_counters(sleep_mock, requests_mock):
    """When the nearest reset falls within `max_wait_time` the limiter waits it out — in
    heartbeat-sized chunks so the platform doesn't see a silent connector — and then reseeds."""
    accepted_waiting_time_in_seconds = 595
    reset_time = int((ab_datetime_now() + timedelta(seconds=accepted_waiting_time_in_seconds)).timestamp())

    requests_mock.get(
        "https://api.github.com/rate_limit",
        json={
            "resources": {
                "core": {"limit": 500, "used": 0, "remaining": 500, "reset": reset_time},
                "graphql": {"limit": 500, "used": 0, "remaining": 500, "reset": reset_time},
            }
        },
    )
    _, authenticator = _source_and_authenticator("token1,token2,token3")
    stream = Organizations(organizations=["org1"], authenticator=authenticator)

    counter_orgs = 0

    def request_callback_orgs(request, context):
        nonlocal counter_orgs
        context.status_code = 200
        while counter_orgs < 1_501:
            counter_orgs += 1
            context.headers = {"Link": '<https://api.github.com/orgs/org1?page=2>; rel="next"', "Content-Type": "application/json"}
            return json.dumps({"id": 1})
        context.headers = {"Content-Type": "application/json"}
        return json.dumps({"id": 2})

    requests_mock.get("https://api.github.com/orgs/org1", text=request_callback_orgs)

    list(read_full_refresh(stream))

    all_sleeps = [c.args[0] for c in sleep_mock.call_args_list]
    assert (
        sum(all_sleeps) >= accepted_waiting_time_in_seconds
    ), f"Expected total sleep >= {accepted_waiting_time_in_seconds}s, got {sum(all_sleeps):.1f}s"
    heartbeat_sleeps = [s for s in all_sleeps if s >= 1.0]
    assert len(heartbeat_sleeps) > 1, "Expected multiple heartbeat sleep chunks, not a single blocking sleep"
    # Counters were reseeded to 500 each after the wait; the two remaining pages were charged
    # against them (the pre-refresh implementation ended on the same 1498 total).
    assert sum(_remaining(authenticator, t) for t in authenticator._tokens) == 1498


def test_invalid_credentials_error_message(requests_mock):
    """Invalid or expired credentials surface an actionable message. Seeding is lazy, so the
    failure appears on the first authenticated request rather than at construction."""
    requests_mock.get(
        "https://api.github.com/rate_limit",
        status_code=401,
        json={"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"},
    )
    _, authenticator = _source_and_authenticator("token1,token2,token3")

    with pytest.raises(AirbyteTracedException) as e:
        authenticator(_prepared_request())

    assert "401" in e.value.message


@freeze_time("2021-01-01 12:00:00")
@patch("time.sleep")
def test_api_budget_throttles_when_tokens_run_low(sleep_mock, requests_mock):
    """Once every token drops below its reserve, small delays spread the remaining calls over
    the time left until reset instead of hitting the wall."""
    low_remaining = 30  # below the default budget_min_reserve of 50
    reset_time = int((ab_datetime_now() + timedelta(seconds=300)).timestamp())

    requests_mock.get(
        "https://api.github.com/rate_limit",
        json={
            "resources": {
                "core": {"limit": 5000, "used": 4970, "remaining": low_remaining, "reset": reset_time},
                "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": reset_time},
            }
        },
    )
    _, authenticator = _source_and_authenticator("token1")

    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    stream = Organizations(organizations=["org1"], authenticator=authenticator)
    list(read_full_refresh(stream))

    assert _remaining(authenticator, "token1") == low_remaining - 1
    assert sleep_mock.call_count >= 1
    for call in sleep_mock.call_args_list:
        assert call.args[0] > 0


@freeze_time("2021-01-01 12:00:00")
@patch("time.sleep")
def test_api_budget_does_not_throttle_with_headroom(sleep_mock, requests_mock):
    reset_time = int((ab_datetime_now() + timedelta(seconds=3600)).timestamp())

    requests_mock.get(
        "https://api.github.com/rate_limit",
        json={
            "resources": {
                "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": reset_time},
                "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": reset_time},
            }
        },
    )
    _, authenticator = _source_and_authenticator("token1")

    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    stream = Organizations(organizations=["org1"], authenticator=authenticator)
    list(read_full_refresh(stream))

    sleep_mock.assert_not_called()


@freeze_time("2021-01-01 12:00:00")
@patch("time.sleep")
def test_api_budget_no_throttle_when_some_tokens_have_headroom(sleep_mock, requests_mock):
    """When only some tokens are below the reserve, rotate to a healthy one instead of slowing down."""
    reset_time = int((ab_datetime_now() + timedelta(seconds=300)).timestamp())
    call_count = 0

    def rate_limit_callback(request, context):
        nonlocal call_count
        call_count += 1
        remaining = 20 if call_count <= 1 else 4000
        return json.dumps(
            {
                "resources": {
                    "core": {"limit": 5000, "used": 5000 - remaining, "remaining": remaining, "reset": reset_time},
                    "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": reset_time},
                }
            }
        )

    requests_mock.get("https://api.github.com/rate_limit", text=rate_limit_callback)
    _, authenticator = _source_and_authenticator("token_low,token_high")

    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    stream = Organizations(organizations=["org1"], authenticator=authenticator)
    list(read_full_refresh(stream))

    sleep_mock.assert_not_called()


def test_rotate_authenticator_token_advances_the_active_token(rate_limit_mock_response):
    _, authenticator = _source_and_authenticator("token1,token2")

    assert authenticator._active_token == "token1"
    assert rotate_authenticator_token(authenticator) is True
    assert authenticator._active_token == "token2"


def test_rotate_authenticator_token_is_a_noop_with_a_single_token(rate_limit_mock_response):
    _, authenticator = _source_and_authenticator("token1")

    assert rotate_authenticator_token(authenticator) is False
    assert authenticator._active_token == "token1"


def test_rotate_authenticator_token_prefers_a_public_cdk_hook(rate_limit_mock_response):
    """The helper reaches into private state only as a fallback; a public rotation API on the
    CDK authenticator takes precedence, so the follow-up swap is a no-op for callers."""
    _, authenticator = _source_and_authenticator("token1,token2")
    calls = []
    authenticator.rotate_token = lambda: calls.append(1)

    assert rotate_authenticator_token(authenticator) is True
    assert calls == [1]
    assert authenticator._active_token == "token1", "the public hook should own rotation"


def test_backoff_strategy_rotates_instead_of_waiting_out_a_long_reset(rate_limit_mock_response):
    _, authenticator = _source_and_authenticator("token1,token2")
    stream = Organizations(organizations=["org1"], authenticator=authenticator)
    strategy = stream.get_backoff_strategy()

    assert strategy.get_waiting_time(15 * 60) == 1
    assert authenticator._active_token == "token2"


def test_backoff_strategy_waits_when_there_is_no_token_to_rotate_to(rate_limit_mock_response):
    """With a single token, returning 1 would busy-retry against a live rate limit."""
    _, authenticator = _source_and_authenticator("token1")
    stream = Organizations(organizations=["org1"], authenticator=authenticator)
    strategy = stream.get_backoff_strategy()

    assert strategy.get_waiting_time(15 * 60) == 15 * 60
