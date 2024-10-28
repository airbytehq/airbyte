#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import sys
import urllib.parse as urlparse

import backoff
from facebook_business.exceptions import FacebookRequestError
from requests.status_codes import codes as status_codes

logger = logging.getLogger("airbyte")


class InstagramAPIException(Exception):
    """General class for all API errors"""


class InstagramExpectedError(InstagramAPIException):
    """Error that we expect to happen, we should continue reading without retrying failed query"""


def retry_pattern(backoff_type, exception, **wait_gen_kwargs):
    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def should_retry_api_error(exc: FacebookRequestError):
        # Retryable OAuth Error Codes
        if exc.api_error_type() == "OAuthException" and exc.api_error_code() in (1, 2, 4, 17, 341, 368):
            return True

        # Rate Limiting Error Codes
        if exc.api_error_code() in (4, 17, 32, 613):
            return True

        if (
            exc.http_status() == status_codes.INTERNAL_SERVER_ERROR
            and exc.api_error_code() == 1
            and exc.api_error_message() == "Please reduce the amount of data you're asking for, then retry your request"
        ):
            return True

        if (
            exc.http_status() == status_codes.INTERNAL_SERVER_ERROR
            and exc.api_error_code() == 1
            and exc.api_error_message() == "An unknown error occurred"
        ):
            return True

        if exc.http_status() == status_codes.TOO_MANY_REQUESTS:
            return True

        if (
            exc.api_error_type() == "OAuthException"
            and exc.api_error_code() == 10
            and exc.api_error_message() == "(#10) Not enough viewers for the media to show insights"
        ):
            return True

        # Issue 4028, Sometimes an error about the Rate Limit is returned with a 400 HTTP code
        if exc.http_status() == status_codes.BAD_REQUEST and exc.api_error_code() == 100 and exc.api_error_subcode() == 33:
            return True

        if exc.api_transient_error():
            return True

        # The media was posted before the most recent time that the user's account
        # was converted to a business account from a personal account.
        if exc.api_error_type() == "OAuthException" and exc.api_error_code() == 100 and exc.api_error_subcode() == 2108006:
            return False

        return False

    return backoff.on_exception(
        backoff_type,
        exception,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=lambda exc: not should_retry_api_error(exc),
        **wait_gen_kwargs,
    )


def remove_params_from_url(url, params):
    parsed = urlparse.urlparse(url)
    query = urlparse.parse_qs(parsed.query, keep_blank_values=True)
    filtered = dict((k, v) for k, v in query.items() if k not in params)
    return urlparse.urlunparse(
        [parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlparse.urlencode(filtered, doseq=True), parsed.fragment]
    )
