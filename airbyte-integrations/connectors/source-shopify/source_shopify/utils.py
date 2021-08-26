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
from time import sleep

import requests


class ShopifyRateLimiter:

    """
    Define timings for RateLimits. Adjust timings if needed.

    :: on_unknown_load = 1.0 sec - Shopify recommended time to hold between each API call.
    :: on_low_load = 0.2 sec (200 miliseconds) - ideal ratio between hold time and api call, also the standard hold time between each API call.
    :: on_mid_load = 1.5 sec - great timing to retrieve another 15% of request capacity while having mid_load.
    :: on_high_load = 5.0 sec - ideally we should wait 2.0 sec while having high_load, but we hold 5 sec to retrieve up to 80% of request capacity.
    """

    on_unknown_load: float = 1.0
    on_low_load: float = 0.2
    on_mid_load: float = 1.5
    on_high_load: float = 5.0

    @staticmethod
    def get_wait_time(*args, threshold: float = 0.9, rate_limit_header: str = "X-Shopify-Shop-Api-Call-Limit"):
        """
        To avoid reaching Shopify API Rate Limits, use the "X-Shopify-Shop-Api-Call-Limit" header value,
        to determine the current rate limits and load and handle wait_time based on load %.
        Recomended wait_time between each request is 1 sec, we would handle this dynamicaly.

        :: threshold - is the % cutoff for the rate_limits % load, if this cutoff is crossed,
                        the connector waits `sleep_on_high_load` amount of time, default value = 0.9 (90%)
        :: wait_time - time between each request = 200 miliseconds
        :: rate_limit_header - responce header item, contains information with rate_limits (current/max)

        Header example:
        {"X-Shopify-Shop-Api-Call-Limit": 10/40}, where: 10 - current load, 40 - max requests capacity.

        More information: https://shopify.dev/api/usage/rate-limits
        """
        # average load based on threshold
        mid_load = threshold / 2
        # find the requests.Response inside args list
        for arg in args:
            response = arg if isinstance(arg, requests.models.Response) else None
        # Get the rate_limits from response
        rate_limits = response.headers.get(rate_limit_header) if response else None
        # define current load from rate_limits
        if rate_limits:
            current_rate, max_rate_limit = rate_limits.split("/")
            load = int(current_rate) / int(max_rate_limit)
        else:
            load = None
        # define wait_time based on load conditions
        if not load:
            # when there is no rate_limits from header, use the `sleep_on_unknown_load`
            wait_time = ShopifyRateLimiter.on_unknown_load
        elif load >= threshold:
            wait_time = ShopifyRateLimiter.on_high_load
        elif load >= mid_load:
            wait_time = ShopifyRateLimiter.on_mid_load
        elif load < mid_load:
            wait_time = ShopifyRateLimiter.on_low_load
        return wait_time

    @staticmethod
    def wait_time(wait_time: float):
        return sleep(wait_time)

    def balance_rate_limit(threshold: float = 0.9, rate_limit_header: str = "X-Shopify-Shop-Api-Call-Limit"):
        """
        The decorator function.
        Adjust `threshold` and `rate_limit_header` if needed.
        """

        def decorator(func):
            @wraps(func)
            def wrapper_balance_rate_limit(*args, **kwargs):
                ShopifyRateLimiter.wait_time(
                    ShopifyRateLimiter.get_wait_time(*args, threshold=threshold, rate_limit_header=rate_limit_header)
                )
                return func(*args, **kwargs)

            return wrapper_balance_rate_limit

        return decorator
