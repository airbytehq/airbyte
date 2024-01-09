#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
import time
from typing import Any, Callable, Coroutine, Mapping, Optional, Type, Union

import aiohttp
import backoff
from requests import HTTPError, PreparedRequest, RequestException, Response, codes, exceptions

from airbyte_cdk.sources.async_cdk.streams.http.exceptions_async import AsyncDefaultBackoffException, AsyncUserDefinedBackoffException
from airbyte_cdk.sources.streams.http.utils import HttpError
from .exceptions import AbstractBaseBackoffException, DefaultBackoffException, UserDefinedBackoffException

TRANSIENT_EXCEPTIONS = (
    DefaultBackoffException,
    AsyncDefaultBackoffException,
    aiohttp.ClientPayloadError,
    aiohttp.ServerTimeoutError,
    aiohttp.ServerConnectionError,
    aiohttp.ServerDisconnectedError,
    exceptions.ConnectTimeout,
    exceptions.ReadTimeout,
    exceptions.ConnectionError,
    exceptions.ChunkedEncodingError,
)

logger = logging.getLogger("airbyte")


AioHttpCallableType = Callable[
    [aiohttp.ClientRequest, Mapping[str, Any]],
    Coroutine[Any, Any, aiohttp.ClientResponse],
]
RequestsCallableType = Callable[[PreparedRequest, Mapping[str, Any]], Response]
SendRequestCallableType = Union[AioHttpCallableType, RequestsCallableType]


def default_backoff_handler(
    max_tries: Optional[int],
    factor: float,
    max_time: Optional[int] = None,
    **kwargs: Any,
) -> Callable[[SendRequestCallableType], SendRequestCallableType]:
    def log_retry_attempt(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, HttpError):
            logger.info(f"Status code: {exc.status_code}, Response Content: {exc.content}")
            logger.info(
                f"Caught retryable error '{exc.message}' after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
            )

        if isinstance(exc, RequestException):
            exc = HttpError(requests_error=exc)

            logger.info(
                f"Caught retryable error '{str(exc)}' after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
            )

    def should_give_up(exc: Exception) -> bool:
        # If a non-rate-limiting related 4XX error makes it this far, it means it was unexpected and probably consistent, so we shouldn't back off
        if isinstance(exc, HttpError):
            give_up: bool = (
                exc.status_code != codes.too_many_requests and 400 <= exc.status_code < 500
            )
            status_code = exc.status_code

        elif isinstance(exc, RequestException):
            # TODO: wrap synchronous codepath's errors in HttpError to delete this path
            give_up: bool = (
                exc.response is not None and exc.response.status_code != codes.too_many_requests and 400 <= exc.response.status_code < 500
            )
            status_code = exc.response if exc else None

        else:
            status_code = None
            give_up = True

        if give_up:
            logger.info(f"Giving up for returned HTTP status: {status_code}")

        # Only RequestExceptions and HttpExceptions are retryable, so if we get here, it's not retryable
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


def _make_user_defined_backoff_handler(
    exc_type: Type[AbstractBaseBackoffException], max_tries: Optional[int], max_time: Optional[int] = None, **kwargs: Any
) -> Callable[[SendRequestCallableType], SendRequestCallableType]:
    def sleep_on_ratelimit(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, exc_type):
            if isinstance(exc, HttpError):
                logger.info(f"Status code: {exc.status_code}, Response Content: {exc.content}")
            elif exc.response:
                logger.info(f"Status code: {exc.response.status_code}, Response Content: {exc.response.content}")

            retry_after = exc.backoff
            logger.info(f"Retrying. Sleeping for {retry_after} seconds")
            time.sleep(retry_after + 1)  # extra second to cover any fractions of second

    def log_give_up(details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        if isinstance(exc, RequestException):
            exc = HttpError(requests_error=exc)
        if isinstance(exc, (HTTPError, HttpError)):
            logger.error(
                f"Max retry limit reached. Request: {exc.request}, Response: {exc.response}"
            )
        else:
            logger.error("Max retry limit reached for unknown request and response")

    return backoff.on_exception(
        backoff.constant,
        exc_type,
        interval=0,  # skip waiting, we'll wait in on_backoff handler
        on_backoff=sleep_on_ratelimit,
        on_giveup=log_give_up,
        jitter=None,
        max_tries=max_tries,
        max_time=max_time,
        **kwargs,
    )

user_defined_backoff_handler = lambda *args, **kwargs: _make_user_defined_backoff_handler(UserDefinedBackoffException, *args, **kwargs)
async_user_defined_backoff_handler = lambda *args, **kwargs: _make_user_defined_backoff_handler(AsyncUserDefinedBackoffException, *args, **kwargs)
