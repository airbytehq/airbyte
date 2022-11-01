#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import http.client
import logging
import sys
from typing import Any

import backoff
import pendulum
from facebook_business.exceptions import FacebookRequestError

# The Facebook API error codes indicating rate-limiting are listed at
# https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
FACEBOOK_RATE_LIMIT_ERROR_CODES = (4, 17, 32, 613, 80000, 80001, 80002, 80003, 80004, 80005, 80006, 80008)
FACEBOOK_TEMPORARY_OAUTH_ERROR_CODE = 2
FACEBOOK_BATCH_ERROR_CODE = 960
FACEBOOK_UNKNOWN_ERROR_CODE = 99
FACEBOOK_CONNECTION_RESET_ERROR_CODE = 104
DEFAULT_SLEEP_INTERVAL = pendulum.duration(minutes=1)

logger = logging.getLogger("airbyte")


class JobException(Exception):
    """Scheduled job failed"""


def retry_pattern(backoff_type, exception, **wait_gen_kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def reduce_request_record_limit(details):
        _, exc, _ = sys.exc_info()
        if (
            details.get("kwargs", {}).get("params", {}).get("limit")
            and exc.http_status() == http.client.INTERNAL_SERVER_ERROR
            and exc.api_error_message() == "Please reduce the amount of data you're asking for, then retry your request"
        ):
            details["kwargs"]["params"]["limit"] = int(int(details["kwargs"]["params"]["limit"]) / 2)

    def should_retry_api_error(exc):
        if isinstance(exc, FacebookRequestError):
            call_rate_limit_error = exc.api_error_code() in FACEBOOK_RATE_LIMIT_ERROR_CODES
            temporary_oauth_error = exc.api_error_code() == FACEBOOK_TEMPORARY_OAUTH_ERROR_CODE
            batch_timeout_error = exc.http_status() == http.client.BAD_REQUEST and exc.api_error_code() == FACEBOOK_BATCH_ERROR_CODE
            unknown_error = exc.api_error_subcode() == FACEBOOK_UNKNOWN_ERROR_CODE
            connection_reset_error = exc.api_error_code() == FACEBOOK_CONNECTION_RESET_ERROR_CODE
            server_error = exc.http_status() == http.client.INTERNAL_SERVER_ERROR
            return any(
                (
                    exc.api_transient_error(),
                    unknown_error,
                    call_rate_limit_error,
                    batch_timeout_error,
                    connection_reset_error,
                    temporary_oauth_error,
                    server_error,
                )
            )
        return True

    return backoff.on_exception(
        backoff_type,
        exception,
        jitter=None,
        on_backoff=[log_retry_attempt, reduce_request_record_limit],
        giveup=lambda exc: not should_retry_api_error(exc),
        **wait_gen_kwargs,
    )


def deep_merge(a: Any, b: Any) -> Any:
    """Merge two values, with `b` taking precedence over `a`."""
    if isinstance(a, dict) and isinstance(b, dict):
        # set of all keys in both dictionaries
        keys = set(a.keys()) | set(b.keys())

        return {key: deep_merge(a.get(key), b.get(key)) for key in keys}
    elif isinstance(a, list) and isinstance(b, list):
        return [*a, *b]
    elif isinstance(a, set) and isinstance(b, set):
        return a | b
    else:
        return a if b is None else b
