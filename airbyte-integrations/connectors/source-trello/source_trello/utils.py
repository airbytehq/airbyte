#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from functools import wraps
from time import sleep

import requests
from airbyte_cdk import AirbyteLogger


class TrelloRequestRateLimits:
    @staticmethod
    def balance_rate_limit(threshold: float = 0.5, rate_limits_headers=None):
        """
        To avoid reaching Trello API Rate Limits, use the rate limits header value,
        to determine the current rate limits and load and handle sleep time based on load %.
        Recommended sleep time between each request is 9 sec.
        Header example:
        {
            x-rate-limit-api-token-interval-ms: 10000
            x-rate-limit-api-token-max: 100
            x-rate-limit-api-token-remaining: 80
            x-rate-limit-api-key-interval-ms: 10000
            x-rate-limit-api-key-max: 300
            x-rate-limit-api-key-remaining: 100
        }
        More information: https://developer.atlassian.com/cloud/trello/guides/rest-api/rate-limits/
        """

        # Define standard timings in seconds
        if rate_limits_headers is None:
            rate_limits_headers = [
                ("x-rate-limit-api-key-remaining", "x-rate-limit-api-key-max"),
                ("x-rate-limit-api-token-remaining", "x-rate-limit-api-token-max"),
            ]

        sleep_on_high_load: float = 9.0

        def decorator(func):
            @wraps(func)
            def wrapper_balance_rate_limit(*args, **kwargs):
                sleep_time = 0
                free_load = float("inf")
                # find the Response inside args list
                for arg in args:
                    response = arg if type(arg) is requests.models.Response else None

                # Get the rate_limits from response
                rate_limits = (
                    [
                        (response.headers.get(rate_remaining_limit_header), response.headers.get(rate_max_limit_header))
                        for rate_remaining_limit_header, rate_max_limit_header in rate_limits_headers
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
                    sleep_time = sleep_on_high_load

                # sleep based on load conditions
                sleep(sleep_time)
                AirbyteLogger().info(f"Sleep {sleep_time} seconds based on load conditions.")

                return func(*args, **kwargs)

            return wrapper_balance_rate_limit

        return decorator
