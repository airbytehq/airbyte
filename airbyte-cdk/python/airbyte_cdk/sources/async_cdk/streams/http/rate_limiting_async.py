#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
import time
from typing import Any, Callable, Coroutine, Mapping, Optional

import aiohttp
import backoff

from airbyte_cdk.sources.streams.http.utils import HttpError
from .exceptions_async import DefaultBackoffException, UserDefinedBackoffException

TRANSIENT_EXCEPTIONS = (
    DefaultBackoffException,
    # TODO
    # exceptions.ConnectTimeout,
    # exceptions.ReadTimeout,
    # exceptions.ConnectionError,
    # exceptions.ChunkedEncodingError,
    aiohttp.ClientPayloadError,
    aiohttp.ServerTimeoutError,
    aiohttp.ServerConnectionError,
    aiohttp.ServerDisconnectedError,
)

logger = logging.getLogger("airbyte")


SendRequestCallableType = Callable[
    [aiohttp.ClientRequest, Mapping[str, Any]],
    Coroutine[Any, Any, aiohttp.ClientResponse],
]
TOO_MANY_REQUESTS_CODE = 429


def default_backoff_handler(
    max_tries: Optional[int],
    factor: float,
    max_time: Optional[int] = None,
    **kwargs: Any,
) -> Callable[[SendRequestCallableType], SendRequestCallableType]:
    def log_retry_attempt(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, HttpError):
            logger.info(
                f"Status code: {exc.status_code}, Response Content: {exc.content}"
            )
        message = exc.message if hasattr(exc, "message") else type(exc)
        logger.info(
            f"Caught retryable error '{message}' after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        )

    def should_give_up(exc: Exception) -> bool:
        # If a non-rate-limiting related 4XX error makes it this far, it means it was unexpected and probably consistent, so we shouldn't back off
        if isinstance(exc, HttpError):
            give_up: bool = (
                exc.status_code != TOO_MANY_REQUESTS_CODE
                and 400 <= exc.status_code < 500
            )
            if give_up:
                logger.info(f"Giving up for returned HTTP status: {exc.status}")
            return give_up
        # Only RequestExceptions are retryable, so if we get here, it's not retryable
        return False

    return backoff.on_exception(
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


def user_defined_backoff_handler(
    max_tries: Optional[int], max_time: Optional[int] = None, **kwargs: Any
) -> Callable[[SendRequestCallableType], SendRequestCallableType]:
    def sleep_on_ratelimit(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, UserDefinedBackoffException):
            logger.info(
                f"Status code: {exc.status_code}, Response Content: {exc.content}"
            )
            retry_after = exc.backoff
            logger.info(f"Retrying. Sleeping for {retry_after} seconds")
            time.sleep(retry_after + 1)  # extra second to cover any fractions of second

    def log_give_up(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, HttpError):
            logger.error(
                f"Max retry limit reached. Request: {exc.url}, Response: {exc.content}"
            )  # TODO: how does history get printed out
        else:
            logger.error("Max retry limit reached for unknown request and response")

    return backoff.on_exception(
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
