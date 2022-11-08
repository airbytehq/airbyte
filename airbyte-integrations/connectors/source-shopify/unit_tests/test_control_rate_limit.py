#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import requests
from source_shopify.utils import ShopifyRateLimiter as limiter

TEST_DATA_FIELD = "some_data_field"
TEST_RATE_LIMIT_HEADER = "X-Shopify-Shop-Api-Call-Limit"
TEST_THRESHOLD = 0.9


def test_with_unknown_load(requests_mock):
    """
    Test simulates the case with unknown load because of missing rate limit header.
    In this case we should wait 1.0 sec sleep before next API call.
    """
    test_response_header = {"no_rate_limit_header": "no_values"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_unknown_load == actual_sleep_time


def test_with_low_load(requests_mock):
    """
    Test simulates low load 10/40 points of rate limit.
    In this case we should wait at least 0.2 sec before next API call.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "10/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_low_load == actual_sleep_time


def test_with_mid_load(requests_mock):
    """
    Test simulates mid load 25/40 points of rate limit.
    In this case we should wait 0.5 sec sleep before next API call.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "25/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_mid_load == actual_sleep_time


def test_with_high_load(requests_mock):
    """
    Test simulates high load 39/40 points of rate limit.
    In this case we should wait 5.0 sec sleep before next API call.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "39/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = limiter.get_wait_time(test_response, threshold=TEST_THRESHOLD, rate_limit_header=TEST_RATE_LIMIT_HEADER)

    assert limiter.on_high_load == actual_sleep_time
