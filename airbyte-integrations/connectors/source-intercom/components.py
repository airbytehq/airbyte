#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from functools import wraps
from time import sleep
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, FailureType, ResponseAction
from airbyte_cdk.sources.types import Record, StreamSlice


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


class ResetCursorSignal:
    """
    Singleton class that manages a reset signal for Intercom's companies stream.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.reset_signal = False
        return cls._instance

    def is_reset_triggered(self) -> bool:
        return self.reset_signal

    def trigger_reset(self) -> None:
        self.reset_signal = True

    def clear_reset(self) -> None:
        self.reset_signal = False


class IntercomErrorHandler(DefaultErrorHandler):
    """
    Custom error handler that triggers a reset on HTTP 500 errors.
    """

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == 500:
            reset_signal = ResetCursorSignal()
            reset_signal.trigger_reset()
            return ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.transient_error,
                error_message="HTTP 500 encountered. Triggering reset to retry from the beginning...",
            )
        return super().interpret_response(response_or_exception)


class IntercomScrollRetriever(SimpleRetriever):
    """
    Custom retriever for Intercom's companies stream with reset handling. Only compatible with streams that sync using
    a single date time window instead of multiple windows when the step is defined. This is okay for the companies stream
    since it only allows for single-threaded processing.

    For the companies stream, we need to implement a custom retriever since we cannot simply retry on HTTP 500 errors.
    Instead, the stream must restart from the beginning to ensure data integrity. See Docs:
    https://developers.intercom.com/docs/references/2.1/rest-api/companies/iterating-over-all-companies
    We need to implement a 'RESTART' action to restart the stream from the beginning in the CDK, which is tracked here:
    https://github.com/airbytehq/airbyte-internal-issues/issues/12107. However, the team does not have the bandwidth
    to implement this at the moment, so this custom component provides a workaround by resetting the cursor on errors.
    """

    RESET_TOKEN = {"_ab_reset": True}

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.reset_signal = ResetCursorSignal()

    def _next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any],
    ) -> Optional[Mapping[str, Any]]:
        """
        Determines the next page token or signals a reset.
        """
        if self.reset_signal.is_reset_triggered():
            self.reset_signal.clear_reset()
            return self.RESET_TOKEN

        next_token = self._paginator.next_page_token(
            response=response,
            last_page_size=last_page_size,
            last_record=last_record,
            last_page_token_value=last_page_token_value,
        )

        return next_token

    def _read_pages(
        self,
        records_generator_fn: Callable[[Optional[requests.Response]], Iterable[Record]],
        stream_state: Mapping[str, Any],
        stream_slice: StreamSlice,
    ) -> Iterable[Record]:
        """
        Reads pages with pagination and reset handling using _next_page_token.
        """
        pagination_complete = False
        initial_token = self._paginator.get_initial_token()
        next_page_token = {"next_page_token": initial_token} if initial_token is not None else None

        while not pagination_complete:
            # Needed for _next_page_token
            response = self.requester.send_request(
                path=self._paginator_path(next_page_token=next_page_token),
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
                request_headers=self._request_headers(next_page_token=next_page_token),
                request_params=self._request_params(next_page_token=next_page_token),
                request_body_data=self._request_body_data(next_page_token=next_page_token),
                request_body_json=self._request_body_json(next_page_token=next_page_token),
            )

            for record in records_generator_fn(response):
                yield record

            if not response:
                pagination_complete = True
            else:
                next_page_token = self._next_page_token(
                    response=response,
                    last_page_size=0,  # Simplified, not tracking size here
                    last_record=None,  # Not needed for reset logic
                    last_page_token_value=(next_page_token.get("next_page_token") if next_page_token else None),
                )
                if next_page_token == self.RESET_TOKEN:
                    next_page_token = {"next_page_token": initial_token} if initial_token is not None else None
                elif not next_page_token:
                    pagination_complete = True

        yield from []


class IntercomScrollPagination(CursorPaginationStrategy):
    """
    Custom pagination strategy for Intercom's companies stream. Only compatible with streams that sync using
    a single date time window instead of multiple windows when the step is defined. This is okay for the companies stream
    since it only allows for single-threaded processing.

    The only change is the stop condtion logic, which is done by comparing the
    token value with the last page token value. If they are equal, we stop the pagination. This is needed since the Intercom API does not
    have any clear stop condition for pagination, and we need to rely on the token value to determine when to stop.

    As of 5/12/25 - they have some fields used for pagination stop conditons but they always result in null values, so we cannot rely on them.
    Ex:
    {
        "type": "list",
        "data": [
            {...}
        ],
        "pages": null,
        "total_count": null,
        "scroll_param": "6287df44-6323-4dfa-8d19-eae43fdc4ab2" <- The scroll param also remains even if there are no more pages; leading to infinite pagination.
    }
    """

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any] = None,
    ) -> Optional[Any]:
        decoded_response = next(self.decoder.decode(response))
        # The default way that link is presented in requests.Response is a string of various links (last, next, etc). This
        # is not indexable or useful for parsing the cursor, so we replace it with the link dictionary from response.links
        headers: Dict[str, Any] = dict(response.headers)
        headers["link"] = response.links
        token = self._cursor_value.eval(
            config=self.config,
            response=decoded_response,
            headers=headers,
            last_record=last_record,
            last_page_size=last_page_size,
        )

        if token == last_page_token_value:
            return None  # stop pagination

        return token if token else None
