#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from functools import wraps
from time import sleep
from typing import Dict

import requests


class IntercomRateLimiter:
    """
    Define timings for RateLimits. Adjust timings if needed.

    :: on_unknown_load = 1.0 sec - Intercom recommended time to hold between each API call.
    :: on_low_load = 0.2 sec (200 miliseconds) - ideal ratio between hold time and api call, also the standard hold time between each API call.
    :: on_mid_load = 1.5 sec - great timing to retrieve another 15% of request capacity while having mid_load.
    :: on_high_load = 5.0 sec - ideally we should wait 2.0 sec while having high_load, but we hold 5 sec to retrieve up to 80% of request capacity.
    """

    on_unknown_load: float = 1.0
    on_low_load: float = 0.1
    on_mid_load: float = 1.5
    on_high_load: float = 10.0

    threshold: float = 0.1

    @staticmethod
    def get_wait_time(
        *args,
        threshold: float = threshold,
        rate_limit_header: str = "X-RateLimit-Limit",
        rate_limit_remain_header: str = "X-RateLimit-Remaining",
    ):
        """
        To avoid reaching Intercom API Rate Limits, use the 'X-RateLimit-Limit','X-RateLimit-Remaining' header values,
        to determine the current rate limits and load and handle wait_time based on load %.
        Recomended wait_time between each request is 1 sec, we would handle this dynamicaly.

        :: threshold - is the % cutoff for the rate_limits % load, if this cutoff is crossed,
                        the connector waits `sleep_on_high_load` amount of time, default value = 0.1 (10% left from max capacity)
        :: wait_time - time between each request = 200 miliseconds
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
        max_rate_limit = int(headers.get(rate_limit_header, 0)) if headers else None
        current_rate = int(headers.get(rate_limit_remain_header, 0)) if headers else None
        # define current load and mid_load from rate_limits
        if current_rate and max_rate_limit:
            mid_load = (max_rate_limit / 2) / max_rate_limit
            load = current_rate / max_rate_limit
        else:
            # to guarantee mid_load value is 0.5 if headers are not available
            mid_load = threshold * 10
            load = None
        # define wait_time based on load conditions
        if not load:
            # when there is no rate_limits from header, use the `sleep_on_unknown_load`
            wait_time = IntercomRateLimiter.on_unknown_load
        elif load <= threshold:
            wait_time = IntercomRateLimiter.on_high_load
        elif load <= mid_load:
            wait_time = IntercomRateLimiter.on_mid_load
        elif load > mid_load:
            wait_time = IntercomRateLimiter.on_low_load
        return wait_time

    @staticmethod
    def wait_time(wait_time: float):
        return sleep(wait_time)

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
                IntercomRateLimiter.wait_time(
                    IntercomRateLimiter.get_wait_time(
                        *args, threshold=threshold, rate_limit_header=rate_limit_header, rate_limit_remain_header=rate_limit_remain_header
                    )
                )
                return func(*args, **kwargs)

            return wrapper_balance_rate_limit

        return decorator


class EagerlyCachedStreamState:
    """
    This is the placeholder for the tmp stream state for each incremental stream,
    It's empty, once the sync has started and is being updated while sync operation takes place,
    It holds the `temporary stream state values` before they are updated to have the opportunity to reuse this state.
    """

    cached_state: Dict = {}

    @staticmethod
    def stream_state_to_tmp(*args, state_object: Dict = cached_state, **kwargs) -> Dict:
        """
        Method to save the current stream state for future re-use within slicing.
        The method requires having the temporary `state_object` as placeholder.
        Because of the specific of Intercom entities relations, we have the opportunity to fetch the updates,
        for particular stream using the `Incremental Refresh`, inside slicing.
        For example:
            if `Conversation Parts` stream records were updated, then the `Conversations` is updated as well
        """
        # Map the input *args, the sequece should be always keeped up to the input function
        # change the mapping if needed
        stream: object = args[0]  # the self instance of the stream
        current_stream_state: Dict = kwargs["stream_state"] or {}
        # get the current tmp_state_value
        tmp_stream_state_value = state_object.get(stream.name, {}).get(stream.cursor_field, "")
        # Save the curent stream value for current sync, if present.
        if current_stream_state:
            state_object[stream.name] = {stream.cursor_field: current_stream_state.get(stream.cursor_field, "")}
            # Check if we have the saved state and keep the minimun value
            if tmp_stream_state_value:
                state_object[stream.name] = {
                    stream.cursor_field: min(current_stream_state.get(stream.cursor_field, ""), tmp_stream_state_value)
                }

        return state_object

    def cache_stream_state(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            EagerlyCachedStreamState.stream_state_to_tmp(*args, **kwargs)
            return func(*args, **kwargs)

        return decorator
