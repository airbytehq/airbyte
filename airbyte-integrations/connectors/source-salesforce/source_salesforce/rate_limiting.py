#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys

import backoff
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from requests import codes, exceptions  # type: ignore[import]

TRANSIENT_EXCEPTIONS = (
    DefaultBackoffException,
    exceptions.ConnectTimeout,
    exceptions.ReadTimeout,
    exceptions.ConnectionError,
    exceptions.HTTPError,
    # We've had a couple of customers with ProtocolErrors, namely:
    # * A self-managed instance during `BulkSalesforceStream.download_data`. This customer had an abnormally high number of ConnectionError
    #   which seems to indicate problems with his network infrastructure in general. The exact error was: `urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(905 bytes read, 119 more expected)', IncompleteRead(905 bytes read, 119 more expected))`
    # * A cloud customer with very long syncs. All those syncs would end up with the following error: `urllib3.exceptions.ProtocolError: ("Connection broken: InvalidChunkLength(got length b'', 0 bytes read)", InvalidChunkLength(got length b'', 0 bytes read))`
    # Without much more information, we will make it retryable hoping that performing the same request will work.
    exceptions.ChunkedEncodingError,
    # We've had examples where the response from Salesforce was not a JSON response. Those cases where error cases though. For example:
    # https://github.com/airbytehq/airbyte-internal-issues/issues/6855. We will assume that this is an edge issue and that retry should help
    exceptions.JSONDecodeError,
)

_RETRYABLE_400_STATUS_CODES = {
    # Using debug mode and breakpointing on the issue, we were able to validate that there issues are retryable. We've also opened a case
    # with Salesforce to try to understand what is causing that as the response does not have a body.
    406,
    # Most of the time, they don't have a body but there was one from the Salesforce Edge mentioning "We are setting things up. This process
    # can take a few minutes. This page will auto-refresh when ready. If it takes too long, please contact support or visit our <a>status
    # page</a> for more information." We therefore assume this is a transient error and will retry on it.
    420,
    codes.too_many_requests,
}


logger = logging.getLogger("airbyte")


def default_backoff_handler(max_tries: int, backoff_method=None, backoff_params=None):
    if backoff_method is None or backoff_params is None:
        if not (backoff_method is None and backoff_params is None):
            raise ValueError("Both `backoff_method` and `backoff_params` need to be provided if one is provided")
        backoff_method = backoff.expo
        backoff_params = {"factor": 15}

    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying...")

    def should_give_up(exc):
        give_up = (
            exc.response is not None
            and exc.response.status_code not in _RETRYABLE_400_STATUS_CODES
            and 400 <= exc.response.status_code < 500
        )

        # Salesforce can return an error with a limit using a 403 code error.
        if exc.response is not None and exc.response.status_code == codes.forbidden:
            error_data = exc.response.json()[0]
            if error_data.get("errorCode", "") == "REQUEST_LIMIT_EXCEEDED":
                give_up = True

        if give_up:
            logger.info(f"Giving up for returned HTTP status: {exc.response.status_code}, body: {exc.response.text}")
        return give_up

    return backoff.on_exception(
        backoff_method,
        TRANSIENT_EXCEPTIONS,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=should_give_up,
        max_tries=max_tries,
        **backoff_params,
    )
