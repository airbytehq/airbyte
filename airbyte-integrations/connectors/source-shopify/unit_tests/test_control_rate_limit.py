#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from functools import wraps

import requests

# Define standard timings in seconds
SLEEP_ON_LOW_LOAD: float = 0.2
SLEEP_ON_AVG_LOAD: float = 1.5
SLEEP_ON_HIGH_LOAD: float = 5.0
SLEEP_ON_UNKNOWN_LOAD: float = 1.0

TEST_HEADER_NAME = "X-Shopify-Shop-Api-Call-Limit"
TEST_DATA_FIELD = "some_data_field"
TEST_RATE_LIMIT_THRESHOLD = 0.9


def control_request_rate_limit_decorator(threshold: float = 0.95, limit_header: str = None):

    """
    This decorator was replicated completely, as separeted function in order to be tested.
    The only difference is:
    :: the real one inside utils.py sleeps the actual defined time and returns the function back,
    :: and this fake one simply sleeps and returns the wait_time as actual sleep time in order to be tested.
    """

    def decorator(func):
        @wraps(func)
        def wrapper_control_request_rate_limit(*args, **kwargs):
            # average load based on threshold
            avg_load = threshold / 2
            # find the Responce inside args list
            for arg in args:
                response = arg if type(arg) is requests.models.Response else None

            # Get the rate_limits from response
            rate_limits = response.headers.get(limit_header) if response else None

            # define current load from rate_limits
            if rate_limits:
                current_rate, max_rate_limit = rate_limits.split("/")
                load = int(current_rate) / int(max_rate_limit)
            else:
                load = None

            # define sleep time based on load conditions
            if not load:
                # when there is no rate_limits from header,
                # use the SLEEP_ON_UNKNOWN_LOAD = 1.0 sec
                wait_time = SLEEP_ON_UNKNOWN_LOAD
            elif load >= threshold:
                wait_time = SLEEP_ON_HIGH_LOAD
            elif load >= avg_load < threshold:
                wait_time = SLEEP_ON_AVG_LOAD
            elif load < avg_load:
                wait_time = SLEEP_ON_LOW_LOAD

            # for this test RETURN wait_time based on load conditions
            return wait_time

        return wrapper_control_request_rate_limit

    return decorator


# Simulating real function call based CDK's parse_response() method
@control_request_rate_limit_decorator(TEST_RATE_LIMIT_THRESHOLD, TEST_HEADER_NAME)
def fake_parse_response(response: requests.Response, **kwargs):
    json_response = response.json()
    records = json_response.get(TEST_DATA_FIELD, []) if TEST_DATA_FIELD is not None else json_response
    yield from records


def test_with_unknown_load(requests_mock):
    """
    Test simulates the case with unknown load because of missing rate limit header.
    In this case we should wait 1.0 sec sleep before next API call.
    """
    test_response_header = {"no_rate_limit_header": "no_values"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = fake_parse_response(test_response)

    assert SLEEP_ON_UNKNOWN_LOAD == actual_sleep_time


def test_with_low_load(requests_mock):
    """
    Test simulates low load 10/40 points of rate limit.
    In this case we should wait at least 0.2 sec before next API call.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "10/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = fake_parse_response(test_response)

    assert SLEEP_ON_LOW_LOAD == actual_sleep_time


def test_with_avg_load(requests_mock):
    """
    Test simulates average load 25/40 points of rate limit.
    In this case we should wait 0.5 sec sleep before next API call.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "25/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = fake_parse_response(test_response)

    assert SLEEP_ON_AVG_LOAD == actual_sleep_time


def test_with_high_load(requests_mock):
    """
    Test simulates high load 39/40 points of rate limit.
    In this case we should wait 5.0 sec sleep before next API call.
    """
    test_response_header = {"X-Shopify-Shop-Api-Call-Limit": "39/40"}

    requests_mock.get("https://test.myshopify.com/", headers=test_response_header)
    test_response = requests.get("https://test.myshopify.com/")

    actual_sleep_time = fake_parse_response(test_response)

    assert SLEEP_ON_HIGH_LOAD == actual_sleep_time
