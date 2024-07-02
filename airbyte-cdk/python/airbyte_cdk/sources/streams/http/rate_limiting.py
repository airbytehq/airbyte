#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
import time
from typing import Any, Callable, Mapping, Optional

import backoff
from requests import PreparedRequest, RequestException, Response, codes, exceptions

from .exceptions import DefaultBackoffException, UserDefinedBackoffException

TRANSIENT_EXCEPTIONS = (
    DefaultBackoffException,
    exceptions.ConnectTimeout,
    exceptions.ReadTimeout,
    exceptions.ConnectionError,
    exceptions.ChunkedEncodingError,
)

logger = logging.getLogger("airbyte")


SendRequestCallableType = Callable[[PreparedRequest, Mapping[str, Any]], Response]


def default_backoff_handler(
    max_tries: Optional[int], factor: float, max_time: Optional[int] = None, **kwargs: Any
) -> Callable[[SendRequestCallableType], SendRequestCallableType]:
    def log_retry_attempt(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, RequestException) and exc.response:
            logger.info(f"Status code: {exc.response.status_code!r}, Response Content: {exc.response.content!r}")
        logger.info(
            f"Caught retryable error '{str(exc)}' after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        )

    def should_give_up(exc: Exception) -> bool:
        # If a non-rate-limiting related 4XX error makes it this far, it means it was unexpected and probably consistent, so we shouldn't back off
        if isinstance(exc, RequestException):
            if exc.response is not None:
                give_up: bool = (
                    exc.response is not None
                    and exc.response.status_code != codes.too_many_requests
                    and 400 <= exc.response.status_code < 500
                )
                if give_up:
                    logger.info(f"Giving up for returned HTTP status: {exc.response.status_code!r}")
                return give_up
        # Only RequestExceptions are retryable, so if we get here, it's not retryable
        return False

    return backoff.on_exception(  # type: ignore # Decorator function returns a function with a different signature than the input function, so mypy can't infer the type of the returned function
        backoff.expo,
        TRANSIENT_EXCEPTIONS,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=should_give_up,
        max_tries=max_tries,
        max_time=max_time,
        factor=factor,
        **kwargs,
    )


def http_client_default_backoff_handler(
    max_tries: Optional[int], max_time: Optional[int] = None, **kwargs: Any
) -> Callable[[SendRequestCallableType], SendRequestCallableType]:
    def log_retry_attempt(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, RequestException) and exc.response:
            logger.info(f"Status code: {exc.response.status_code!r}, Response Content: {exc.response.content!r}")
        logger.info(
            f"Caught retryable error '{str(exc)}' after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        )

    def should_give_up(exc: Exception) -> bool:
        # If made it here, the ResponseAction was RETRY and therefore should not give up
        return False

    return backoff.on_exception(  # type: ignore # Decorator function returns a function with a different signature than the input function, so mypy can't infer the type of the returned function
        backoff.expo,
        TRANSIENT_EXCEPTIONS,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=should_give_up,
        max_tries=max_tries,
        max_time=max_time,
        **kwargs,
    )


def user_defined_backoff_handler(
    max_tries: Optional[int], max_time: Optional[int] = None, **kwargs: Any
) -> Callable[[SendRequestCallableType], SendRequestCallableType]:
    def sleep_on_ratelimit(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, UserDefinedBackoffException):
            if exc.response:
                logger.info(f"Status code: {exc.response.status_code!r}, Response Content: {exc.response.content!r}")
            retry_after = exc.backoff
            logger.info(f"Retrying. Sleeping for {retry_after} seconds")
            time.sleep(retry_after + 1)  # extra second to cover any fractions of second

    def log_give_up(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, RequestException):
            logger.error(f"Max retry limit reached in {details['elapsed']}s. Request: {exc.request}, Response: {exc.response}")
        else:
            logger.error("Max retry limit reached for unknown request and response")

    return backoff.on_exception(  # type: ignore # Decorator function returns a function with a different signature than the input function, so mypy can't infer the type of the returned function
        backoff.constant,
        UserDefinedBackoffException,
        interval=0,  # skip waiting, we'll wait in on_backoff handler
        on_backoff=sleep_on_ratelimit,
        on_giveup=log_give_up,
        jitter=None,
        max_tries=max_tries,
        max_time=max_time,
        **kwargs,
    )
