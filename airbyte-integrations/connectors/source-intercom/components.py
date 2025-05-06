#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from functools import wraps
from time import sleep
from typing import Any, Mapping, Optional, Union, Iterable

import requests

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, FailureType, ResponseAction
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.types import Record


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


class SubstreamStateMigration(StateMigration):
    """
    We require a custom state migration to move from the custom substream state that was generated via the legacy
    cursor custom components. State was not written back to the platform in a way that is compatible with concurrent cursors.

    The old state roughly had the following shape:
    {
        "updated_at": 1744153060,
        "prior_state": {
            "updated_at": 1744066660
        }
        "conversations": {
            "updated_at": 1744153060
        }
    }

    However, this was incompatible when we removed the custom cursors with the concurrent substream partition cursor
    components that were configured with use global_substream_cursor and incremental_dependency. They rely on passing the value
    of parent_state when getting parent records for the conversations/companies parent stream. The migration results in state:
    {
        "updated_at": 1744153060,
        "prior_state": {
            "updated_at": 1744066660
            # There are a lot of nested elements here, but are not used or relevant to syncs
        }
        "conversations": {
            "updated_at": 1744153060
        }
        "parent_state": {
            "conversations": {
                "updated_at": 1744153060
            }
        }
    }
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "parent_state" not in stream_state and ("conversations" in stream_state or "companies" in stream_state)

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        migrated_parent_state = {}
        if stream_state.get("conversations"):
            migrated_parent_state["conversations"] = stream_state.get("conversations")
        if stream_state.get("companies"):
            migrated_parent_state["companies"] = stream_state.get("companies")
        return {**stream_state, "parent_state": migrated_parent_state}


class CursorManager:
    """
    Singleton class that manages the cursor state exclusively for Intercom's companies stream. It provides methods to get, update,
    and reset the cursor, which tracks the scroll position for iterating over companies. The singleton pattern ensures a single,
    shared cursor state across the sync process.
    
    For the companies stream, we need to implement a custom retriever since we cannot simply retry on HTTP 500 errors.
    Instead, the stream must restart from the beginning to ensure data integrity. See Docs:
    https://developers.intercom.com/docs/references/2.1/rest-api/companies/iterating-over-all-companies
    
    We need to implement a 'RESTART' action to restart the stream from the beginning in the CDK, which is tracked here:
    https://github.com/airbytehq/airbyte-internal-issues/issues/12107. However, the team does not have the bandwidth
    to implement this at the moment, so this custom component provides a workaround by resetting the cursor on errors.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cursor = None
        return cls._instance

    def get_cursor(self) -> Optional[str]:
        return self.cursor
    
    def update_cursor(self, new_cursor: str) -> None:
        self.cursor = new_cursor

    def reset(self) -> None:
        self.cursor = None


class IntercomErrorHandler(DefaultErrorHandler):
    """
    Custom error handler that overrides the default behavior for HTTP 500 errors. When a 500 error occurs, it resets the cursor
    using the CursorManager and triggers a retry, allowing the sync to restart from the beginning. For all other errors, it delegates
    to the parent class’s handling logic.
    """
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == 500:
            cursor_manager = CursorManager()
            cursor_manager.reset()
            resolution = ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.transient_error,
                error_message="The companies stream has faced an HTTP 500. Retrying from the first scroll...",
            )
            return resolution
        return super().interpret_response(response_or_exception)


class CursorManagerAwarePaginationStrategy(CursorPaginationStrategy):
    """
    Extends the standard cursor pagination strategy by integrating with the CursorManager. After determining the next page token
    from the response, it updates the CursorManager with this token if it exists, ensuring the cursor state reflects the latest
    pagination position for subsequent requests.
    """
    def next_page_token(self, response, last_page_size: int, last_record: Optional[Record], last_page_token_value: Optional[Any] = None):
        next_token = super().next_page_token(response=response, last_page_size=last_page_size, last_record=last_record)
        cursor_manager = CursorManager()
        if next_token is not None:
            cursor_manager.update_cursor(next_token)
        return next_token


class CursorAwareSinglePartitionRouter(SinglePartitionRouter):
    """
    Custom router that generates a single stream slice based on the current cursor state from the CursorManager. It includes the
    cursor as a `scroll_param` in the partition, enabling the retriever to request the correct page of data during the sync process.
    """
    def __init__(self, parameters: Mapping[str, Any]):
        super().__init__(parameters)
        self.cursor_manager = CursorManager()

    def stream_slices(self) -> Iterable[StreamSlice]:
        cursor = self.cursor_manager.get_cursor()
        slice = StreamSlice(partition={"scroll_param": cursor}, cursor_slice={})
        yield slice


class IntercomScrollRetriever(SimpleRetriever):
    """
    Custom retriever that overrides the default stream slicer with a CursorAwareSinglePartitionRouter during initialization.
    This ensures that pagination is driven by cursor-based stream slices, allowing the sync to progress based on the managed cursor state.
    """
    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.stream_slicer = CursorAwareSinglePartitionRouter(parameters)