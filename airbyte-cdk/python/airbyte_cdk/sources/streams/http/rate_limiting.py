#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import sys
import time
from typing import Optional

import backoff
from requests import codes, exceptions

from .exceptions import DefaultBackoffException, UserDefinedBackoffException

TRANSIENT_EXCEPTIONS = (DefaultBackoffException, exceptions.ConnectTimeout, exceptions.ReadTimeout, exceptions.ConnectionError)

logger = logging.getLogger("airbyte")


def default_backoff_handler(max_tries: Optional[int], factor: float, **kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        if exc.response:
            logger.info(f"Status code: {exc.response.status_code}, Response Content: {exc.response.content}")
        logger.info(
            f"Caught retryable error '{str(exc)}' after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        )

    def should_give_up(exc):
        # If a non-rate-limiting related 4XX error makes it this far, it means it was unexpected and probably consistent, so we shouldn't back off
        give_up = exc.response is not None and exc.response.status_code != codes.too_many_requests and 400 <= exc.response.status_code < 500
        if give_up:
            logger.info(f"Giving up for returned HTTP status: {exc.response.status_code}")
        return give_up

    return backoff.on_exception(
        backoff.expo,
        TRANSIENT_EXCEPTIONS,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=should_give_up,
        max_tries=max_tries,
        factor=factor,
        **kwargs,
    )


def user_defined_backoff_handler(max_tries: Optional[int], **kwargs):
    def sleep_on_ratelimit(details):
        _, exc, _ = sys.exc_info()
        if isinstance(exc, UserDefinedBackoffException):
            if exc.response:
                logger.info(f"Status code: {exc.response.status_code}, Response Content: {exc.response.content}")
            retry_after = exc.backoff
            logger.info(f"Retrying. Sleeping for {retry_after} seconds")
            time.sleep(retry_after + 1)  # extra second to cover any fractions of second

    def log_give_up(details):
        _, exc, _ = sys.exc_info()
        logger.error(f"Max retry limit reached. Request: {exc.request}, Response: {exc.response}")

    return backoff.on_exception(
        backoff.constant,
        UserDefinedBackoffException,
        interval=0,  # skip waiting, we'll wait in on_backoff handler
        on_backoff=sleep_on_ratelimit,
        on_giveup=log_give_up,
        jitter=None,
        max_tries=max_tries,
        **kwargs,
    )
