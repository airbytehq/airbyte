#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import sys
from typing import Union

import backoff
from airbyte_cdk.logger import AirbyteLogger
from chargebee.api_error import InvalidRequestError, OperationFailedError
from requests import codes

TRANSIENT_EXCEPTIONS = (
    OperationFailedError,
    InvalidRequestError,
)

logger = AirbyteLogger()


def default_backoff_handler(max_tries: int, factor: int, **kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying...")

    def should_give_up(exc: Union[OperationFailedError, InvalidRequestError]):
        give_up = (exc.http_status_code != codes.too_many_requests and 400 <= exc.http_status_code < 500) or (
            exc.http_status_code == codes.service_unavailable and exc.api_error_code == "site_not_ready"
        )
        if give_up:
            logger.info(f"Giving up for returned HTTP status: `{exc.http_status_code}` and `api_error_code`: `{exc.api_error_code}`")
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
