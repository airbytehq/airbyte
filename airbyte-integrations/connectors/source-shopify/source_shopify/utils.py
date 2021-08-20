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


class ShopifyRequestRateLimits(object):

    @staticmethod
    def balance_rate_limit(threshold: float = 0.9, rate_limit_header: str = "X-Shopify-Shop-Api-Call-Limit"):
        """
        To avoid reaching Shopify API Rate Limits, use the "X-Shopify-Shop-Api-Call-Limit" header value,
        to determine the current rate limits and load and handle wait_time based on load %.
        Recomended wait_time between each request is 1 sec, we would handle this dynamicaly.

        :: wait_time time between each request - 100 miliseconds

        Header example:
        {"X-Shopify-Shop-Api-Call-Limit": 10/40}, where: 10 - current load, 40 - max requests capacity.

        More information: https://shopify.dev/api/usage/rate-limits
        """

        # Define standard timings in seconds
        sleep_on_low_load: float = 0.2
        sleep_on_avg_load: float = 1.5
        sleep_on_high_load: float = 5.0
        sleep_on_unknown_load: float = 1.0

        def decorator(func):
            @wraps(func)
            def wrapper_balance_rate_limit(*args, **kwargs):
                # average load based on threshold
                avg_load = threshold / 2
                # find the requests.Response inside args list
                for arg in args:
                    response = arg if type(arg) is requests.models.Response else None

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
                    # when there is no rate_limits from header,
                    # use the 1.0 sec
                    wait_time = sleep_on_unknown_load
                elif load >= threshold:
                    wait_time = sleep_on_high_load
                elif load >= avg_load < threshold:
                    wait_time = sleep_on_avg_load
                elif load < avg_load:
                    wait_time = sleep_on_low_load

                # sleep based on load conditions
                sleep(wait_time)

                return func(*args, **kwargs)

            return wrapper_balance_rate_limit

        return decorator
