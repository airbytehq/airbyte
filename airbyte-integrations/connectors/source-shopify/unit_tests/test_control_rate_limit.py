#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import requests
from source_shopify.utils import ShopifyRateLimiter as limiter


TEST_DATA_FIELD = "some_data_field"
TEST_RATE_LIMIT_HEADER = "X-Shopify-Shop-Api-Call-Limit"
TEST_THRESHOLD = 0.9


def get_graphql_api_response(maximum_available, currently_available):
    """
    Mock the json returned by graphql request
    """
    return {
        "extensions": {
            "cost": {
                "requestedQueryCost": 72,
                "actualQueryCost": 3,
                "throttleStatus": {
                    "maximumAvailable": maximum_available,
                    "currentlyAvailable": currently_available,
                    "restoreRate": 100.0,
                },
            }
        }
    }


def test_rest_api_with_unknown_load(requests_mock):
    """
    Test simulates the case with unknown load because of missing rate limit header.
    """
    test_response_header = {"no_rate_limit_header": "no_values"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_rest_api_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_unknown_load == actual_sleep_time


def test_rest_api_with_very_low_load(requests_mock):
    """
    Test simulates very low load 2/40 points of rate limit.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "1/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_rest_api_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_very_low_load == actual_sleep_time


def test_rest_api_with_low_load(requests_mock):
    """
    Test simulates low load 10/40 points of rate limit.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "10/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_rest_api_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_low_load == actual_sleep_time


def test_rest_api_with_mid_load(requests_mock):
    """
    Test simulates mid load 25/40 points of rate limit.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "25/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_rest_api_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_mid_load == actual_sleep_time


def test_rest_api_with_high_load(requests_mock):
    """
    Test simulates high load 39/40 points of rate limit.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "39/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_rest_api_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_high_load == actual_sleep_time


def test_graphql_api_with_unknown_load(requests_mock):
    """
    Test simulates the case with unknown load because the json body is missing for an unknown reason.
    """
    requests_mock.get("https://test.myshopify.com/", json={})
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_graphql_api_wait_time(test_response, threshold=TEST_THRESHOLD)

    assert limiter.on_unknown_load == actual_sleep_time


def test_graphql_api_with_very_low_load(requests_mock):
    """
    Test simulates very low load (2000-1800)/2000=0.1 points of rate limit.
    """

    api_response = get_graphql_api_response(maximum_available=2000, currently_available=1800)
    requests_mock.get("https://test.myshopify.com/", json=api_response)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_graphql_api_wait_time(test_response, threshold=TEST_THRESHOLD)

    assert limiter.on_very_low_load == actual_sleep_time


def test_graphql_api_with_low_load(requests_mock):
    """
    Test simulates low load (2000-1500)/2000=0.25 points of rate limit.
    """

    api_response = get_graphql_api_response(maximum_available=2000, currently_available=1500)
    requests_mock.get("https://test.myshopify.com/", json=api_response)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_graphql_api_wait_time(test_response, threshold=TEST_THRESHOLD)

    assert limiter.on_low_load == actual_sleep_time


def test_graphql_api_with_mid_load(requests_mock):
    """
    Test simulates mid load (2000-1000)/2000=0.5 points of rate limit.
    """
    api_response = get_graphql_api_response(maximum_available=2000, currently_available=1000)
    requests_mock.get("https://test.myshopify.com/", json=api_response)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_graphql_api_wait_time(test_response, threshold=TEST_THRESHOLD)

    assert limiter.on_mid_load == actual_sleep_time


def test_graphql_api_with_high_load(requests_mock):
    """
    Test simulates high load (2000-100)/2000=0.95 points of rate limit.
    """
    api_response = get_graphql_api_response(maximum_available=2000, currently_available=100)
    requests_mock.get("https://test.myshopify.com/", json=api_response)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_graphql_api_wait_time(test_response, threshold=TEST_THRESHOLD)

    assert limiter.on_high_load == actual_sleep_time
