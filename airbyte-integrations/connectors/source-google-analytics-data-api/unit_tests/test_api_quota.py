#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from source_google_analytics_data_api.api_quota import GoogleAnalyticsApiQuota

from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


TEST_QUOTA_INSTANCE: GoogleAnalyticsApiQuota = GoogleAnalyticsApiQuota()


@pytest.fixture(name="expected_quota_list")
def expected_quota_list():
    """The Quota were currently handle"""
    return ["concurrentRequests", "tokensPerProjectPerHour", "potentiallyThresholdedRequestsPerHour"]


def test_check_initial_quota_is_empty():
    """
    Check the initial quota property is empty (== None), but ready to be fullfield.
    """
    assert not TEST_QUOTA_INSTANCE.initial_quota


@pytest.mark.parametrize(
    ("response_quota", "partial_quota", "response_action_exp", "backoff_time_exp", "stop_iter_exp"),
    [
        # Full Quota
        (
            {
                "propertyQuota": {
                    "concurrentRequests": {"consumed": 0, "remaining": 10},
                    "tokensPerProjectPerHour": {"consumed": 1, "remaining": 1735},
                    "potentiallyThresholdedRequestsPerHour": {"consumed": 1, "remaining": 26},
                }
            },
            False,  # partial_quota
            ResponseAction.RETRY,
            None,  # backoff_time_exp
            False,  # stop_iter_exp
        ),
        # Partial Quota
        (
            {
                "propertyQuota": {
                    "concurrentRequests": {"consumed": 0, "remaining": 10},
                    "tokensPerProjectPerHour": {"consumed": 5, "remaining": 955},
                    "potentiallyThresholdedRequestsPerHour": {"consumed": 3, "remaining": 26},
                }
            },
            True,  # partial_quota
            ResponseAction.RETRY,
            None,  # backoff_time_exp
            False,  # stop_iter_exp
        ),
        # Running out `tokensPerProjectPerHour`
        (
            {
                "propertyQuota": {
                    "concurrentRequests": {"consumed": 2, "remaining": 8},
                    "tokensPerProjectPerHour": {
                        "consumed": 5,
                        # ~9% from original quota is left
                        "remaining": 172,
                    },
                    "potentiallyThresholdedRequestsPerHour": {"consumed": 3, "remaining": 26},
                }
            },
            True,  # partial_quota
            ResponseAction.RETRY,
            1800,  # backoff_time_exp
            False,  # stop_iter_exp
        ),
        # Running out `concurrentRequests`
        (
            {
                "propertyQuota": {
                    "concurrentRequests": {
                        "consumed": 9,
                        # 10% from original quota is left
                        "remaining": 1,
                    },
                    "tokensPerProjectPerHour": {"consumed": 5, "remaining": 935},
                    "potentiallyThresholdedRequestsPerHour": {"consumed": 1, "remaining": 26},
                }
            },
            True,  # partial_quota
            ResponseAction.RETRY,
            30,  # backoff_time_exp
            False,  # stop_iter_exp
        ),
        # Running out `potentiallyThresholdedRequestsPerHour`
        (
            {
                "propertyQuota": {
                    "concurrentRequests": {"consumed": 1, "remaining": 9},
                    "tokensPerProjectPerHour": {"consumed": 5, "remaining": 935},
                    "potentiallyThresholdedRequestsPerHour": {
                        # 7% from original quota is left
                        "consumed": 26,
                        "remaining": 2,
                    },
                }
            },
            True,  # partial_quota
            ResponseAction.RETRY,
            1800,  # backoff_time_exp
            False,  # stop_iter_exp
        ),
    ],
    ids=[
        "Full",
        "Partial",
        "Running out tokensPerProjectPerHour",
        "Running out concurrentRequests",
        "Running out potentiallyThresholdedRequestsPerHour",
    ],
)
def test_check_full_quota(
    requests_mock,
    expected_quota_list,
    response_quota,
    partial_quota,
    response_action_exp,
    backoff_time_exp,
    stop_iter_exp,
):
    """
    Check the quota and prepare the initial values for subsequent comparison with subsequent response calls.
    The default values for the scenario are expected when the quota is full.
    """
    # Prepare instance
    url = "https://analyticsdata.googleapis.com/v1beta/"
    payload = response_quota
    requests_mock.post(url, json=payload)
    response = requests.post(url)
    # process and prepare the scenario
    TEST_QUOTA_INSTANCE._check_quota(response)

    # TEST BLOCK

    # Check the INITIAL QUOTA is saved properly
    assert [quota in expected_quota_list for quota in TEST_QUOTA_INSTANCE.initial_quota.keys()]

    # Check the CURRENT QUOTA is different from Initial
    if partial_quota:
        current_quota = TEST_QUOTA_INSTANCE._get_known_quota_from_response(response.json().get("propertyQuota"))
        assert not current_quota == TEST_QUOTA_INSTANCE.initial_quota

    # Check the scenario is applied based on Quota Values
    assert TEST_QUOTA_INSTANCE.response_action is response_action_exp
    # backoff_time
    assert TEST_QUOTA_INSTANCE.backoff_time == backoff_time_exp
    # stop_iter
    assert TEST_QUOTA_INSTANCE.stop_iter is stop_iter_exp
