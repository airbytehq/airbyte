#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from functools import wraps
from time import sleep
from typing import Mapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution


RequestInput = Union[str, Mapping[str, str]]


@dataclass
class IntercomRateLimiter:
    """
    Define timings for RateLimits. Adjust timings if needed.
    :: on_unknown_load = 1.0 sec - Intercom recommended time to hold between each API call.
    :: on_low_load = 0.01 sec (10 miliseconds) - ideal ratio between hold time and api call, also the standard hold time between each API call.
    :: on_mid_load = 1.5 sec - great timing to retrieve another 15% of request capacity while having mid_load.
    :: on_high_load = 8.0 sec - ideally we should wait 5.0 sec while having high_load, but we hold 8 sec to retrieve up to 80% of request capacity.
    """

    threshold: float = 0.1
    on_unknown_load: float = 1.0
    on_low_load: float = 0.01
    on_mid_load: float = 1.5
    on_high_load: float = 8.0  # max time

    @staticmethod
    def backoff_time(backoff_time: float):
        return sleep(backoff_time)

    @staticmethod
    def _define_values_from_headers(
        current_rate_header_value: Optional[float],
        total_rate_header_value: Optional[float],
        threshold: float = threshold,
    ) -> tuple[float, Union[float, str]]:
        # define current load and cutoff from rate_limits
        if current_rate_header_value and total_rate_header_value:
            cutoff: float = (total_rate_header_value / 2) / total_rate_header_value
            load: float = current_rate_header_value / total_rate_header_value
        else:
            # to guarantee cutoff value to be exactly 1 sec, based on threshold, if headers are not available
            cutoff: float = threshold * (1 / threshold)
            load = None
        return cutoff, load

    @staticmethod
    def _convert_load_to_backoff_time(
        cutoff: float,
        load: Optional[float] = None,
        threshold: float = threshold,
    ) -> float:
        # define backoff_time based on load conditions
        if not load:
            backoff_time = IntercomRateLimiter.on_unknown_load
        elif load <= threshold:
            backoff_time = IntercomRateLimiter.on_high_load
        elif load <= cutoff:
            backoff_time = IntercomRateLimiter.on_mid_load
        elif load > cutoff:
            backoff_time = IntercomRateLimiter.on_low_load
        return backoff_time

    @staticmethod
    def get_backoff_time(
        *args,
        threshold: float = threshold,
        rate_limit_header: str = "X-RateLimit-Limit",
        rate_limit_remain_header: str = "X-RateLimit-Remaining",
    ):
        """
        To avoid reaching Intercom API Rate Limits, use the 'X-RateLimit-Limit','X-RateLimit-Remaining' header values,
        to determine the current rate limits and load and handle backoff_time based on load %.
        Recomended backoff_time between each request is 1 sec, we would handle this dynamicaly.
        :: threshold - is the % cutoff for the rate_limits % load, if this cutoff is crossed,
                        the connector waits `sleep_on_high_load` amount of time, default value = 0.1 (10% left from max capacity)
        :: backoff_time - time between each request = 200 miliseconds
        :: rate_limit_header - responce header item, contains information with max rate_limits available (max)
        :: rate_limit_remain_header - responce header item, contains information with how many requests are still available (current)
        Header example:
        {
            X-RateLimit-Limit: 100
            X-RateLimit-Remaining: 51
            X-RateLimit-Reset: 1487332510
        },
            where: 51 - requests remains and goes down, 100 - max requests capacity.
        More information: https://developers.intercom.com/intercom-api-reference/reference/rate-limiting
        """

        # find the requests.Response inside args list
        for arg in args:
            if isinstance(arg, requests.models.Response):
                headers = arg.headers or {}

        # Get the rate_limits from response
        total_rate = int(headers.get(rate_limit_header, 0)) if headers else None
        current_rate = int(headers.get(rate_limit_remain_header, 0)) if headers else None
        cutoff, load = IntercomRateLimiter._define_values_from_headers(
            current_rate_header_value=current_rate,
            total_rate_header_value=total_rate,
            threshold=threshold,
        )

        backoff_time = IntercomRateLimiter._convert_load_to_backoff_time(cutoff=cutoff, load=load, threshold=threshold)
        return backoff_time

    @staticmethod
    def balance_rate_limit(
        threshold: float = threshold,
        rate_limit_header: str = "X-RateLimit-Limit",
        rate_limit_remain_header: str = "X-RateLimit-Remaining",
    ):
        """
        The decorator function.
        Adjust `threshold`,`rate_limit_header`,`rate_limit_remain_header` if needed.
        """

        def decorator(func):
            @wraps(func)
            def wrapper_balance_rate_limit(*args, **kwargs):
                IntercomRateLimiter.backoff_time(
                    IntercomRateLimiter.get_backoff_time(
                        *args, threshold=threshold, rate_limit_header=rate_limit_header, rate_limit_remain_header=rate_limit_remain_header
                    )
                )
                return func(*args, **kwargs)

            return wrapper_balance_rate_limit

        return decorator


class ErrorHandlerWithRateLimiter(DefaultErrorHandler):
    """
    The difference between the built-in `DefaultErrorHandler` and this one is the custom decorator,
    applied on top of `interpret_response` to preserve the api calls for a defined amount of time,
    calculated using the rate limit headers and not use the custom backoff strategy,
    since we deal with Response.status_code == 200,
    the default requester's logic doesn't allow to handle the status of 200 with `should_retry()`.
    """

    # The RateLimiter is applied to balance the api requests.
    @IntercomRateLimiter.balance_rate_limit()
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        # Check for response.headers to define the backoff time before the next api call
        return super().interpret_response(response_or_exception)
