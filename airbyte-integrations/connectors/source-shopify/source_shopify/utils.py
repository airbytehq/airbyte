#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import enum
import logging
from functools import wraps
from time import sleep
from typing import Any, Callable, Dict, Final, List, Mapping, Optional

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction
from airbyte_cdk.utils import AirbyteTracedException


# default logger instance
LOGGER: Final[logging.Logger] = logging.getLogger("airbyte")


class ShopifyNonRetryableErrors:
    """Holds the errors classification and messaging scenarios."""

    def __new__(self, stream: str) -> Mapping[str, Any]:
        return {
            401: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message=f"Stream `{stream}`. Failed to access the Shopify store with provided API token. Verify your API token is valid.",
            ),
            402: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message=f"Stream `{stream}`. The shop's plan does not have access to this feature. Please upgrade your plan to be  able to access this stream.",
            ),
            403: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message=f"Stream `{stream}`. Unable to access Shopify endpoint for {stream}. Check that you have the appropriate access scopes to read data from this endpoint.",
            ),
            404: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message=f"Stream `{stream}`. Not available or missing.",
            ),
            500: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message=f"Stream `{stream}`. Entity might not be available or missing.",
            ),
            # extend the mapping with more handable errors, if needed.
        }


class ShopifyAccessScopesError(AirbyteTracedException):
    """Raises the error if authenticated user doesn't have access to verify the grantted scopes."""

    help_url = "https://shopify.dev/docs/api/usage/access-scopes#authenticated-access-scopes"

    def __init__(self, response, **kwargs) -> None:
        self.message = f"Reason: Scopes are not available, make sure you're using the correct `Shopify Store` name. Actual response: {response}. More info about: {self.help_url}"
        super().__init__(internal_message=self.message, failure_type=FailureType.config_error, **kwargs)


class ShopifyBadJsonError(AirbyteTracedException):
    """Raises the error when Shopify replies with broken json for `access_scopes` request"""

    def __init__(self, message, **kwargs) -> None:
        self.message = f"Reason: Bad JSON Response from the Shopify server. Details: {message}."
        super().__init__(internal_message=self.message, failure_type=FailureType.transient_error, **kwargs)


class ShopifyConnectionError(AirbyteTracedException):
    """Raises the error when Shopify resources couldn't be accessed because of the ConnectionError occured (100-x)"""

    def __init__(self, details, **kwargs) -> None:
        self.message = f"Invalid `Shopify Store` name used or `host` couldn't be verified by Shopify. Details: {details}"
        super().__init__(internal_message=self.message, failure_type=FailureType.config_error, **kwargs)


class ShopifyWrongShopNameError(AirbyteTracedException):
    """Raises the error when `Shopify Store` name is incorrect or couldn't be verified by the Shopify"""

    def __init__(self, url, **kwargs) -> None:
        self.message = f"The `Shopify Store` name is invalid or missing for `input configuration`, make sure it's valid. Details: {url}"
        super().__init__(internal_message=self.message, failure_type=FailureType.config_error, **kwargs)


class UnrecognisedApiType(Exception):
    pass


class ApiTypeEnum(enum.Enum):
    rest = "rest"
    graphql = "graphql"

    @classmethod
    def api_types(cls) -> List:
        return [api_type.value for api_type in ApiTypeEnum]


class ShopifyRateLimiter:
    """
    Define timings for RateLimits. Adjust timings if needed.

    :: on_unknown_load = 1.0 sec - Shopify recommended time to hold between each API call.
    :: on_low_load = 0.2 sec (200 miliseconds) - ideal ratio between hold time and api call, also the standard hold time between each API call.
    :: on_mid_load = 1.5 sec - great timing to retrieve another 15% of request capacity while having mid_load.
    :: on_high_load = 5.0 sec - ideally we should wait 2.0 sec while having high_load, but we hold 5 sec to retrieve up to 80% of request capacity.
    """

    on_unknown_load: float = 1.0
    on_very_low_load: float = 0.0
    on_low_load: float = 0.2
    on_mid_load: float = 1.5
    on_high_load: float = 5.0

    log_message_count = 0
    log_message_frequency = 3

    def log_message_counter(message: str) -> None:
        """
        Print the rate-limit info message every `log_message_frequency` request, to minimize the noise in the logs.
        """
        if ShopifyRateLimiter.log_message_count < ShopifyRateLimiter.log_message_frequency:
            ShopifyRateLimiter.log_message_count += 1
        else:
            LOGGER.info(message)
            ShopifyRateLimiter.log_message_count = 0

    def get_response_from_args(*args) -> Optional[requests.Response]:
        for arg in args:
            if isinstance(arg, requests.models.Response):
                return arg

    @staticmethod
    def _convert_load_to_time(load: Optional[float], threshold: float) -> float:
        """
        Define wait_time based on load conditions.

        :: load - represents how close we are to being throttled
            - 0.5 is half way through our allowance
            - 1 indicates that all of the allowance is used and the api will start rejecting calls
        :: threshold - is the % cutoff for the rate_limits/load
        :: wait_time - time to wait between each request in seconds

        """

        half_of_threshold = threshold / 2  # average load based on threshold
        quarter_of_threshold = threshold / 4  # low load based on threshold

        if not load:
            # when there is no rate_limits from header, use the `sleep_on_unknown_load`
            wait_time = ShopifyRateLimiter.on_unknown_load
            ShopifyRateLimiter.log_message_counter("API Load: `REGULAR`")
        elif threshold <= load:
            wait_time = ShopifyRateLimiter.on_high_load
            ShopifyRateLimiter.log_message_counter("API Load: `HIGH`")
        elif half_of_threshold <= load < threshold:
            wait_time = ShopifyRateLimiter.on_mid_load
            ShopifyRateLimiter.log_message_counter("API Load: `MID`")
        elif quarter_of_threshold <= load < half_of_threshold:
            wait_time = ShopifyRateLimiter.on_low_load
            ShopifyRateLimiter.log_message_counter("API Load: `LOW`")
        elif load < quarter_of_threshold:
            wait_time = ShopifyRateLimiter.on_very_low_load

        return wait_time

    @staticmethod
    def get_rest_api_wait_time(
        *args,
        threshold: float = 0.9,
        rate_limit_header: str = "X-Shopify-Shop-Api-Call-Limit",
    ) -> float:
        """
        To avoid reaching Shopify REST API Rate Limits, use the "X-Shopify-Shop-Api-Call-Limit" header value,
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
        # find the requests.Response inside args list
        response = ShopifyRateLimiter.get_response_from_args(*args)
        # Get the rate_limits from response
        rate_limits = response.headers.get(rate_limit_header) if response else None
        # define current load from rate_limits
        if rate_limits:
            current_rate, max_rate_limit = rate_limits.split("/")
            load = int(current_rate) / int(max_rate_limit)
        else:
            load = None
        wait_time = ShopifyRateLimiter._convert_load_to_time(load, threshold)
        return wait_time

    @staticmethod
    def get_graphql_api_wait_time(*args, threshold: float = 0.9) -> float:
        """
        To avoid reaching Shopify Graphql API Rate Limits, use the extensions dict in the response.

        :: threshold - is the % cutoff for the % load, if this cutoff is crossed,
                        the connector waits `sleep_on_high_load` amount of time

        Body example:
        In this example we are 75% through our allowance.
        This is calculated as: ((2000 - 500)/2000)*100= 75
        {
            "data": {...}
            "extensions": {
                "cost": {
                    "requestedQueryCost": 72,
                    "actualQueryCost": 3,
                    "throttleStatus": {
                        "maximumAvailable": 2000.0,
                        "currentlyAvailable": 500,
                        "restoreRate": 100.0
                    }
                }
            }
        }

        More information: https://shopify.dev/api/usage/rate-limits
        """
        # find the requests.Response inside args list
        response = ShopifyRateLimiter.get_response_from_args(*args)

        # Get the rate limit info from response
        if response:
            try:
                throttle_status = response.json()["extensions"]["cost"]["throttleStatus"]
                max_available = throttle_status["maximumAvailable"]
                currently_available = throttle_status["currentlyAvailable"]
                if max_available and currently_available:
                    load = (int(max_available) - int(currently_available)) / int(max_available)
            except KeyError:
                load = None
        else:
            load = None

        wait_time = ShopifyRateLimiter._convert_load_to_time(load, threshold)
        return wait_time

    @staticmethod
    def wait_time(wait_time: float) -> None:
        return sleep(wait_time)

    @staticmethod
    def balance_rate_limit(
        threshold: float = 0.9,
        rate_limit_header: str = "X-Shopify-Shop-Api-Call-Limit",
        api_type: ApiTypeEnum = ApiTypeEnum.rest.value,
    ) -> Callable[..., Any]:
        """
        The decorator function.
        Adjust `threshold`, `rate_limit_header` and `api_type` if needed.
        """

        def decorator(func) -> Callable[..., Any]:
            @wraps(func)
            def wrapper_balance_rate_limit(*args, **kwargs) -> Any:
                if api_type == ApiTypeEnum.rest.value:
                    ShopifyRateLimiter.wait_time(
                        ShopifyRateLimiter.get_rest_api_wait_time(*args, threshold=threshold, rate_limit_header=rate_limit_header)
                    )
                elif api_type == ApiTypeEnum.graphql.value:
                    ShopifyRateLimiter.wait_time(ShopifyRateLimiter.get_graphql_api_wait_time(*args, threshold=threshold))
                else:
                    raise UnrecognisedApiType(f"unrecognised api type: {api_type}. valid values are: {ApiTypeEnum.api_types()}")
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
        Because of the specific of Shopify's entities relations, we have the opportunity to fetch the updates,
        for particular stream using the `Incremental Refresh`, inside slicing.
        For example:
            if `order refund` records were updated, then the `orders` is updated as well.
            if 'transaction` was added to the order, then the `orders` is updated as well.
            etc.
        """
        # Map the input *args, the sequece should be always keeped up to the input function
        # change the mapping if needed
        stream: object = args[0]  # the self instance of the stream
        current_stream_state: Dict = kwargs.get("stream_state") or {}
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

    def cache_stream_state(func) -> Callable[..., Any]:
        @wraps(func)
        def decorator(*args, **kwargs) -> Any:
            EagerlyCachedStreamState.stream_state_to_tmp(*args, **kwargs)
            return func(*args, **kwargs)

        return decorator
