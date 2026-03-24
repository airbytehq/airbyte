#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import timedelta
from unittest.mock import patch

import pytest
import responses
from freezegun import freeze_time
from requests import JSONDecodeError
from source_github import SourceGithub
from source_github.streams import Organizations
from source_github.utils import MultipleTokenAuthenticatorWithRateLimiter, read_full_refresh

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now


@responses.activate
def test_multiple_tokens(rate_limit_mock_response):
    authenticator = SourceGithub()._get_authenticator({"access_token": "token_1, token_2, token_3"})
    assert isinstance(authenticator, MultipleTokenAuthenticatorWithRateLimiter)
    assert ["token_1", "token_2", "token_3"] == list(authenticator._tokens)


def test_authenticator_counter(rate_limit_mock_response, requests_mock):
    """
    This test ensures that the rate limiter:
     1. correctly handles the available limits from GitHub API and saves it.
     2. correctly counts the number of requests made.
    """
    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1", "token2", "token3"])

    assert [(x.count_rest, x.count_graphql) for x in authenticator._tokens.values()] == [(5000, 5000), (5000, 5000), (5000, 5000)]
    organization_args = {"organizations": ["org1", "org2"], "authenticator": authenticator}
    stream = Organizations(**organization_args)
    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    requests_mock.get("https://api.github.com/orgs/org2", json={"id": 2})
    list(read_full_refresh(stream))
    assert authenticator._tokens["token1"].count_rest == 4998


@patch("time.sleep")
def test_multiple_token_authenticator_with_rate_limiter(sleep_mock, requests_mock):
    """
    This test ensures that:
     1. The rate limiter iterates over all tokens one-by-one after the previous is fully drained.
     2. Counter is set to zero after 1500 requests were made. (500 available requests per key were set as default)
     3. Exception is handled and log warning message could be found in output. Connector does not raise AirbyteTracedException because there might be GraphQL streams with remaining request we still can read.
    """

    counter_rate_limits = 0
    counter_orgs = 0

    def request_callback_rate_limits(request, context):
        nonlocal counter_rate_limits
        while counter_rate_limits < 3:
            counter_rate_limits += 1
            resp_body = {
                "resources": {
                    "core": {"limit": 500, "used": 0, "remaining": 500, "reset": 4070908800},
                    "graphql": {"limit": 500, "used": 0, "remaining": 500, "reset": 4070908800},
                }
            }
            context.status_code = 200
            context.headers = {}
            return json.dumps(resp_body)

    requests_mock.get("https://api.github.com/rate_limit", text=request_callback_rate_limits)
    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1", "token2", "token3"])
    organization_args = {"organizations": ["org1"], "authenticator": authenticator}
    stream = Organizations(**organization_args)

    def request_callback_orgs(request, context):
        nonlocal counter_orgs
        while counter_orgs < 1_501:
            counter_orgs += 1
            resp_body = {"id": 1}
            context.headers = {"Link": '<https://api.github.com/orgs/org1?page=2>; rel="next"', "Content-Type": "application/json"}
            context.status_code = 200
            return json.dumps(resp_body)

    requests_mock.get(
        "https://api.github.com/orgs/org1",
        text=request_callback_orgs,
    )
    with pytest.raises(AirbyteTracedException) as e:
        list(read_full_refresh(stream))
    assert [(x.count_rest, x.count_graphql) for x in authenticator._tokens.values()] == [(0, 500), (0, 500), (0, 500)]
    assert e.value.failure_type == FailureType.transient_error
    assert "Stream: `organizations`" in e.value.internal_message
    assert "Rate limits for all tokens" in e.value.internal_message


@freeze_time("2021-01-01 12:00:00")
@patch("time.sleep")
def test_multiple_token_authenticator_with_rate_limiter_and_sleep(sleep_mock, caplog, requests_mock):
    """
    This test ensures that:
     1. The rate limiter will only wait (sleep) for token availability if the nearest available token appears within 600 seconds (see max_time).
     2. Token Counter is reset to new values after 1500 requests were made and last token is still in use.
    """

    counter_rate_limits = 0
    counter_orgs = 0
    ACCEPTED_WAITING_TIME_IN_SECONDS = 595
    reset_time = int((ab_datetime_now() + timedelta(seconds=ACCEPTED_WAITING_TIME_IN_SECONDS)).timestamp())

    def request_callback_rate_limits(request, context):
        nonlocal counter_rate_limits
        while counter_rate_limits < 6:
            counter_rate_limits += 1
            resp_body = {
                "resources": {
                    "core": {"limit": 500, "used": 0, "remaining": 500, "reset": reset_time},
                    "graphql": {"limit": 500, "used": 0, "remaining": 500, "reset": reset_time},
                }
            }
            context.status_code = 200
            context.headers = {}
            return json.dumps(resp_body)

    requests_mock.get("https://api.github.com/rate_limit", text=request_callback_rate_limits)
    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1", "token2", "token3"])
    organization_args = {"organizations": ["org1"], "authenticator": authenticator}
    stream = Organizations(**organization_args)

    def request_callback_orgs(request, context):
        nonlocal counter_orgs
        while counter_orgs < 1_501:
            counter_orgs += 1
            resp_body = {"id": 1}
            context.status_code = 200
            context.headers = {"Link": '<https://api.github.com/orgs/org1?page=2>; rel="next"', "Content-Type": "application/json"}
            return json.dumps(resp_body)
        context.status_code = 200
        context.headers = {"Content-Type": "application/json"}
        return json.dumps({"id": 2})

    requests_mock.get(
        "https://api.github.com/orgs/org1",
        text=request_callback_orgs,
    )

    list(read_full_refresh(stream))
    # The exhaustion sleep (595s) must be present among the calls.
    # Budget-throttle sleeps (small fractional values) may also appear.
    exhaustion_sleeps = [c for c in sleep_mock.call_args_list if c.args[0] == ACCEPTED_WAITING_TIME_IN_SECONDS]
    assert len(exhaustion_sleeps) == 1, f"Expected exactly one exhaustion sleep of {ACCEPTED_WAITING_TIME_IN_SECONDS}s"
    assert [(x.count_rest, x.count_graphql) for x in authenticator._tokens.values()] == [(500, 500), (500, 500), (498, 500)]


def test_invalid_credentials_error_message(requests_mock):
    """
    Test that validates that invalid or expired credentials are gracefully caught and surfaced back in a way
    that the connector can display actionable messages back to users
    """

    requests_mock.get(
        "https://api.github.com/rate_limit",
        status_code=401,
        json={"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"},
    )

    with pytest.raises(AirbyteTracedException) as e:
        MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1", "token2", "token3"])

    assert "HTTP Status Code: 401" in e.value.message


@freeze_time("2021-01-01 12:00:00")
@patch("time.sleep")
def test_api_budget_throttles_when_tokens_run_low(sleep_mock, requests_mock):
    """
    Verify that the API budget mechanism injects small delays once all
    tokens drop below the reserve threshold, preventing full exhaustion.
    """
    low_remaining = 30  # Below BUDGET_MIN_RESERVE (50)
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

    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1"])
    token = authenticator._tokens["token1"]
    assert token.count_rest == low_remaining

    # Simulate a single request — budget throttle should fire because
    # remaining (30) < BUDGET_MIN_RESERVE (50)
    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    organization_args = {"organizations": ["org1"], "authenticator": authenticator}
    stream = Organizations(**organization_args)
    list(read_full_refresh(stream))

    # time.sleep should have been called with a positive delay for throttling
    assert sleep_mock.call_count >= 1
    for call in sleep_mock.call_args_list:
        assert call.args[0] > 0


@freeze_time("2021-01-01 12:00:00")
@patch("time.sleep")
def test_api_budget_does_not_throttle_with_headroom(sleep_mock, requests_mock):
    """
    Verify that no throttling occurs when tokens have plenty of remaining calls.
    """
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

    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1"])
    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    organization_args = {"organizations": ["org1"], "authenticator": authenticator}
    stream = Organizations(**organization_args)
    list(read_full_refresh(stream))

    # No throttle delay should have been introduced
    sleep_mock.assert_not_called()


@freeze_time("2021-01-01 12:00:00")
@patch("time.sleep")
def test_api_budget_no_throttle_when_some_tokens_have_headroom(sleep_mock, requests_mock):
    """
    When only some tokens are below the reserve but others are not, no
    throttling should occur — the connector should just rotate to a
    healthy token.
    """
    reset_time = int((ab_datetime_now() + timedelta(seconds=300)).timestamp())
    call_count = 0

    def rate_limit_callback(request, context):
        nonlocal call_count
        call_count += 1
        # First token: low remaining. Second token: plenty of headroom.
        if call_count <= 1:
            remaining = 20
        else:
            remaining = 4000
        return json.dumps(
            {
                "resources": {
                    "core": {"limit": 5000, "used": 5000 - remaining, "remaining": remaining, "reset": reset_time},
                    "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": reset_time},
                }
            }
        )

    requests_mock.get("https://api.github.com/rate_limit", text=rate_limit_callback)
    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token_low", "token_high"])

    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    organization_args = {"organizations": ["org1"], "authenticator": authenticator}
    stream = Organizations(**organization_args)
    list(read_full_refresh(stream))

    # No throttle — the second token still has headroom
    sleep_mock.assert_not_called()
