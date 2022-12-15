#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from functools import wraps

import requests

# Define standard timings in seconds
SLEEP_ON_HIGH_LOAD: float = 9.0

TEST_DATA_FIELD = "some_data_field"
TEST_RATE_LIMIT_THRESHOLD = 0.1
TEST_HEADERS_NAME = [
    ("x-rate-limit-api-key-remaining", "x-rate-limit-api-key-max"),
    ("x-rate-limit-api-token-remaining", "x-rate-limit-api-token-max"),
]


def control_request_rate_limit_decorator(threshold: float = 0.05, limit_headers=None):
    """
    This decorator was replicated completely, as separeted function in order to be tested.
    The only difference is:
    :: the real one inside utils.py sleeps the actual defined time and returns the function back,
    :: and this fake one simply sleeps and returns the wait_time as actual sleep time in order to be tested.
    """

    def decorator(func):
        @wraps(func)
        def wrapper_control_request_rate_limit(*args, **kwargs):
            sleep_time = 0
            free_load = float("inf")
            # find the Response inside args list
            for arg in args:
                response = arg if type(arg) is requests.models.Response else None

            # Get the rate_limits from response
            rate_limits = (
                [
                    (response.headers.get(rate_remaining_limit_header), response.headers.get(rate_max_limit_header))
                    for rate_remaining_limit_header, rate_max_limit_header in limit_headers
                ]
                if response
                else None
            )

            # define current load from rate_limits
            if rate_limits:
                for current_rate, max_rate_limit in rate_limits:
                    free_load = min(free_load, int(current_rate) / int(max_rate_limit))

            # define sleep time based on load conditions
            if free_load <= threshold:
                sleep_time = SLEEP_ON_HIGH_LOAD

            # for this test RETURN sleep_time based on load conditions
            return sleep_time

        return wrapper_control_request_rate_limit

    return decorator


# Simulating real function call based CDK's parse_response() method
@control_request_rate_limit_decorator(TEST_RATE_LIMIT_THRESHOLD, TEST_HEADERS_NAME)
def fake_parse_response(response: requests.Response, **kwargs):
    json_response = response.json()
    records = json_response.get(TEST_DATA_FIELD, []) if TEST_DATA_FIELD is not None else json_response
    yield from records


def test_with_load(requests_mock):
    """
    Test simulates high load of rate limit.
    In this case we should wait at least 9 sec before next API call.
    """
    test_response_header = {
        "x-rate-limit-api-token-max": "300",
        "x-rate-limit-api-token-remaining": "10",
        "x-rate-limit-api-key-max": "300",
        "x-rate-limit-api-key-remaining": "100",
    }

    requests_mock.get("https://test.trello.com/", headers=test_response_header)
    test_response = requests.get("https://test.trello.com/")

    actual_sleep_time = fake_parse_response(test_response)

    assert SLEEP_ON_HIGH_LOAD == actual_sleep_time
