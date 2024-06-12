#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import http.client
import logging
import re
import sys
from typing import Any

import backoff
import pendulum
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException
from facebook_business.exceptions import FacebookRequestError

# The Facebook API error codes indicating rate-limiting are listed at
# https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
FACEBOOK_RATE_LIMIT_ERROR_CODES = {
    4,
    17,
    32,
    613,
    80000,
    80001,
    80002,
    80003,
    80004,
    80005,
    80006,
    80008,
}
FACEBOOK_TEMPORARY_OAUTH_ERROR_CODE = 2
FACEBOOK_BATCH_ERROR_CODE = 960
FACEBOOK_UNKNOWN_ERROR_CODE = 99
FACEBOOK_CONNECTION_RESET_ERROR_CODE = 104
DEFAULT_SLEEP_INTERVAL = pendulum.duration(minutes=1)

logger = logging.getLogger("airbyte")


class JobException(Exception):
    """Scheduled job failed"""


class AccountTypeException(Exception):
    """Wrong account type"""


def retry_pattern(backoff_type, exception, **wait_gen_kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def reduce_request_record_limit(details):
        _, exc, _ = sys.exc_info()
        # the list of error patterns to track,
        # in order to reduce the request page size and retry
        error_patterns = [
            "Please reduce the amount of data you're asking for, then retry your request",
            "An unknown error occurred",
        ]
        if (
            details.get("kwargs", {}).get("params", {}).get("limit")
            and exc.http_status() == http.client.INTERNAL_SERVER_ERROR
            and exc.api_error_message() in error_patterns
        ):
            # reduce the existing request `limit` param by a half and retry
            details["kwargs"]["params"]["limit"] = int(int(details["kwargs"]["params"]["limit"]) / 2)
            # set the flag to the api class that the last api call failed
            details.get("args")[0].last_api_call_is_successfull = False
            # set the flag to the api class that the `limit` param was reduced
            details.get("args")[0].request_record_limit_is_reduced = True

    def revert_request_record_limit(details):
        """
        This method is triggered `on_success` after successful retry,
        sets the internal class flags to provide the logic to restore the previously reduced
        `limit` param.
        """
        # reference issue: https://github.com/airbytehq/airbyte/issues/25383
        # set the flag to the api class that the last api call was successful
        details.get("args")[0].last_api_call_is_successfull = True
        # set the flag to the api class that the `limit` param is restored
        details.get("args")[0].request_record_limit_is_reduced = False

    def give_up(details):
        if isinstance(details["exception"], FacebookRequestError):
            raise traced_exception(details["exception"])

    def is_transient_cannot_include_error(exc: FacebookRequestError) -> bool:
        """After migration to API v19.0, some customers randomly face a BAD_REQUEST error (OAuthException) with the pattern:"Cannot include ..."
        According to the last comment in https://developers.facebook.com/community/threads/286697364476462/, this might be a transient issue that can be solved with a retry."""
        pattern = r"Cannot include .* in summary param because they weren't there while creating the report run."
        return bool(exc.http_status() == http.client.BAD_REQUEST and re.search(pattern, exc.api_error_message()))

    def should_retry_api_error(exc):
        if isinstance(exc, FacebookRequestError):
            call_rate_limit_error = exc.api_error_code() in FACEBOOK_RATE_LIMIT_ERROR_CODES
            temporary_oauth_error = exc.api_error_code() == FACEBOOK_TEMPORARY_OAUTH_ERROR_CODE
            batch_timeout_error = exc.http_status() == http.client.BAD_REQUEST and exc.api_error_code() == FACEBOOK_BATCH_ERROR_CODE
            unknown_error = exc.api_error_subcode() == FACEBOOK_UNKNOWN_ERROR_CODE
            connection_reset_error = exc.api_error_code() == FACEBOOK_CONNECTION_RESET_ERROR_CODE
            server_error = exc.http_status() == http.client.INTERNAL_SERVER_ERROR
            service_unavailable_error = exc.http_status() == http.client.SERVICE_UNAVAILABLE
            return any(
                (
                    exc.api_transient_error(),
                    unknown_error,
                    call_rate_limit_error,
                    batch_timeout_error,
                    is_transient_cannot_include_error(exc),
                    connection_reset_error,
                    temporary_oauth_error,
                    server_error,
                    service_unavailable_error,
                )
            )
        return True

    return backoff.on_exception(
        backoff_type,
        exception,
        jitter=None,
        on_backoff=[log_retry_attempt, reduce_request_record_limit],
        on_success=[revert_request_record_limit],
        on_giveup=[give_up],
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


def traced_exception(fb_exception: FacebookRequestError):
    """Add user-friendly message for FacebookRequestError

    Please see ../unit_tests/test_errors.py for full error examples
    Please add new errors to the tests
    """
    msg = fb_exception.api_error_message() or fb_exception.get_message()

    if "Error validating access token" in msg:
        failure_type = FailureType.config_error
        friendly_msg = "Invalid access token. Re-authenticate if FB oauth is used or refresh access token with all required permissions"

    elif "(#100) Missing permissions" in msg:
        failure_type = FailureType.config_error
        friendly_msg = (
            "Credentials don't have enough permissions. Check if correct Ad Account Id is used (as in Ads Manager), "
            "re-authenticate if FB oauth is used or refresh access token with all required permissions"
        )

    elif "permission" in msg:
        failure_type = FailureType.config_error
        friendly_msg = (
            "Credentials don't have enough permissions. Re-authenticate if FB oauth is used or refresh access token "
            "with all required permissions."
        )

    elif "An unknown error occurred" in msg and "error_user_title" in fb_exception._error:
        msg = fb_exception._error["error_user_title"]
        if "profile is not linked to delegate page" in msg or "el perfil no est" in msg:
            failure_type = FailureType.config_error
            friendly_msg = (
                "Current profile is not linked to delegate page. Check if correct business (not personal) "
                "Ad Account Id is used (as in Ads Manager), re-authenticate if FB oauth is used or refresh "
                "access token with all required permissions."
            )

    elif fb_exception.api_error_code() in FACEBOOK_RATE_LIMIT_ERROR_CODES:
        return AirbyteTracedException(
            message="The maximum number of requests on the Facebook API has been reached. See https://developers.facebook.com/docs/graph-api/overview/rate-limiting/ for more information",
            internal_message=str(fb_exception),
            failure_type=FailureType.transient_error,
            exception=fb_exception,
        )

    elif fb_exception.http_status() == 503:
        return AirbyteTracedException(
            message="The Facebook API service is temporarily unavailable. This issue should resolve itself, and does not require further action.",
            internal_message=str(fb_exception),
            failure_type=FailureType.transient_error,
            exception=fb_exception,
        )

    else:
        failure_type = FailureType.system_error
        error_code = fb_exception.api_error_code() if fb_exception.api_error_code() else fb_exception.http_status()
        friendly_msg = f"Error code {error_code}: {msg}."

    return AirbyteTracedException(
        message=friendly_msg or msg,
        internal_message=msg,
        failure_type=failure_type,
        exception=fb_exception,
    )
