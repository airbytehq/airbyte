#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import patch

import pendulum
import pytest
import responses
from freezegun import freeze_time
from source_github import SourceGithub
from source_github.streams import Organizations
from source_github.utils import MultipleTokenAuthenticatorWithRateLimiter, read_full_refresh

from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType


@responses.activate
def test_multiple_tokens(rate_limit_mock_response):
    authenticator = SourceGithub()._get_authenticator({"access_token": "token_1, token_2, token_3"})
    assert isinstance(authenticator, MultipleTokenAuthenticatorWithRateLimiter)
    assert ["token_1", "token_2", "token_3"] == list(authenticator._tokens)


@responses.activate
def test_authenticator_counter(rate_limit_mock_response):
    """
    This test ensures that the rate limiter:
     1. correctly handles the available limits from GitHub API and saves it.
     2. correctly counts the number of requests made.
    """
    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1", "token2", "token3"])

    assert [(x.count_rest, x.count_graphql) for x in authenticator._tokens.values()] == [(5000, 5000), (5000, 5000), (5000, 5000)]
    organization_args = {"organizations": ["org1", "org2"], "authenticator": authenticator}
    stream = Organizations(**organization_args)
    responses.add("GET", "https://api.github.com/orgs/org1", json={"id": 1})
    responses.add("GET", "https://api.github.com/orgs/org2", json={"id": 2})
    list(read_full_refresh(stream))
    assert authenticator._tokens["token1"].count_rest == 4998


@responses.activate
def test_multiple_token_authenticator_with_rate_limiter():
    """
    This test ensures that:
     1. The rate limiter iterates over all tokens one-by-one after the previous is fully drained.
     2. Counter is set to zero after 1500 requests were made. (500 available requests per key were set as default)
     3. Exception is handled and log warning message could be found in output. Connector does not raise AirbyteTracedException because there might be GraphQL streams with remaining request we still can read.
    """

    counter_rate_limits = 0
    counter_orgs = 0

    def request_callback_rate_limits(request):
        nonlocal counter_rate_limits
        while counter_rate_limits < 3:
            counter_rate_limits += 1
            resp_body = {
                "resources": {
                    "core": {"limit": 500, "used": 0, "remaining": 500, "reset": 4070908800},
                    "graphql": {"limit": 500, "used": 0, "remaining": 500, "reset": 4070908800},
                }
            }
            return (200, {}, json.dumps(resp_body))

    responses.add_callback(responses.GET, "https://api.github.com/rate_limit", callback=request_callback_rate_limits)
    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1", "token2", "token3"])
    organization_args = {"organizations": ["org1"], "authenticator": authenticator}
    stream = Organizations(**organization_args)

    def request_callback_orgs(request):
        nonlocal counter_orgs
        while counter_orgs < 1_501:
            counter_orgs += 1
            resp_body = {"id": 1}
            headers = {"Link": '<https://api.github.com/orgs/org1?page=2>; rel="next"'}
            return (200, headers, json.dumps(resp_body))

    responses.add_callback(
        responses.GET,
        "https://api.github.com/orgs/org1",
        callback=request_callback_orgs,
        content_type="application/json",
    )
    with pytest.raises(AirbyteTracedException) as e:
        list(read_full_refresh(stream))
    assert [(x.count_rest, x.count_graphql) for x in authenticator._tokens.values()] == [(0, 500), (0, 500), (0, 500)]
    message = (
        "Stream: `organizations`, slice: `{'organization': 'org1'}`. Limits for all provided tokens are reached, please try again later"
    )
    assert e.value.failure_type == FailureType.config_error
    assert e.value.internal_message == message


@freeze_time("2021-01-01 12:00:00")
@responses.activate
@patch("time.sleep")
def test_multiple_token_authenticator_with_rate_limiter_and_sleep(sleep_mock, caplog):
    """
    This test ensures that:
     1. The rate limiter will only wait (sleep) for token availability if the nearest available token appears within 600 seconds (see max_time).
     2. Token Counter is reset to new values after 1500 requests were made and last token is still in use.
    """

    counter_rate_limits = 0
    counter_orgs = 0
    ACCEPTED_WAITING_TIME_IN_SECONDS = 595
    reset_time = (pendulum.now() + pendulum.duration(seconds=ACCEPTED_WAITING_TIME_IN_SECONDS)).int_timestamp

    def request_callback_rate_limits(request):
        nonlocal counter_rate_limits
        while counter_rate_limits < 6:
            counter_rate_limits += 1
            resp_body = {
                "resources": {
                    "core": {"limit": 500, "used": 0, "remaining": 500, "reset": reset_time},
                    "graphql": {"limit": 500, "used": 0, "remaining": 500, "reset": reset_time},
                }
            }
            return (200, {}, json.dumps(resp_body))

    responses.add_callback(responses.GET, "https://api.github.com/rate_limit", callback=request_callback_rate_limits)
    authenticator = MultipleTokenAuthenticatorWithRateLimiter(tokens=["token1", "token2", "token3"])
    organization_args = {"organizations": ["org1"], "authenticator": authenticator}
    stream = Organizations(**organization_args)

    def request_callback_orgs(request):
        nonlocal counter_orgs
        while counter_orgs < 1_501:
            counter_orgs += 1
            resp_body = {"id": 1}
            headers = {"Link": '<https://api.github.com/orgs/org1?page=2>; rel="next"'}
            return (200, headers, json.dumps(resp_body))
        return (200, {}, json.dumps({"id": 2}))

    responses.add_callback(
        responses.GET,
        "https://api.github.com/orgs/org1",
        callback=request_callback_orgs,
        content_type="application/json",
    )

    list(read_full_refresh(stream))
    sleep_mock.assert_called_once_with(ACCEPTED_WAITING_TIME_IN_SECONDS)
    assert [(x.count_rest, x.count_graphql) for x in authenticator._tokens.values()] == [(500, 500), (500, 500), (498, 500)]
