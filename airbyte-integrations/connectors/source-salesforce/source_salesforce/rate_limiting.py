#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import re
import sys
from typing import Any, Mapping, Optional, Union

import backoff
import requests
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, ResponseAction
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_protocol.models import FailureType
from requests import codes, exceptions  # type: ignore[import]

RESPONSE_CONSUMPTION_EXCEPTIONS = (
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

TRANSIENT_EXCEPTIONS = (
    DefaultBackoffException,
    exceptions.ConnectTimeout,
    exceptions.ReadTimeout,
    exceptions.ConnectionError,
    exceptions.HTTPError,
) + RESPONSE_CONSUMPTION_EXCEPTIONS

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
_AUTHENTICATION_ERROR_MESSAGE_MAPPING = {
    "expired access/refresh token": "The authentication to SalesForce has expired. Re-authenticate to restore access to SalesForce."
}


logger = logging.getLogger("airbyte")


class BulkNotSupportedException(Exception):
    pass


class SalesforceErrorHandler(ErrorHandler):
    def __init__(self, stream_name: str = "<unknown stream>", sobject_options: Optional[Mapping[str, Any]] = None) -> None:
        self._stream_name = stream_name
        self._sobject_options: Mapping[str, Any] = sobject_options or {}

    @property
    def max_retries(self) -> Optional[int]:
        return 5

    @property
    def max_time(self) -> Optional[int]:
        return 120

    def interpret_response(self, response: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        if isinstance(response, TRANSIENT_EXCEPTIONS):
            return ErrorResolution(
                ResponseAction.RETRY,
                FailureType.transient_error,
                f"Error of type {type(response)} is considered transient. Try again later. (full error message is {response})",
            )
        elif isinstance(response, requests.Response):
            if response.ok:
                return ErrorResolution(ResponseAction.IGNORE, None, None)

            if not (400 <= response.status_code < 500) or response.status_code in _RETRYABLE_400_STATUS_CODES:
                return ErrorResolution(
                    ResponseAction.RETRY,
                    FailureType.transient_error,
                    f"Response with status code {response.status_code} is considered transient. Try again later. (full error message is {response.content})",
                )

            error_code, error_message = self._extract_error_code_and_message(response)
            if self._is_login_request(response):
                return ErrorResolution(
                    ResponseAction.FAIL,
                    FailureType.config_error,
                    _AUTHENTICATION_ERROR_MESSAGE_MAPPING.get(error_message)
                    if error_message in _AUTHENTICATION_ERROR_MESSAGE_MAPPING
                    else f"An error occurred: {response.content.decode()}",
                )

            if self._is_bulk_job_creation(response) and response.status_code in [codes.FORBIDDEN, codes.BAD_REQUEST]:
                return self._handle_bulk_job_creation_endpoint_specific_errors(response, error_code, error_message)

            if response.status_code == codes.too_many_requests or (
                response.status_code == codes.forbidden and error_code == "REQUEST_LIMIT_EXCEEDED"
            ):
                # It is unclear as to why we don't retry on those. The rate limit window is 24 hours but it is rolling so we could end up being able to sync more records before 24 hours. Note that there is also a limit of concurrent long running requests which can fall in this bucket.
                return ErrorResolution(
                    ResponseAction.FAIL,
                    FailureType.transient_error,
                    f"Request limit reached with HTTP status {response.status_code}. body: {response.text}",
                )

            if (
                "We can't complete the action because enabled transaction security policies took too long to complete." in error_message
                and error_code == "TXN_SECURITY_METERING_ERROR"
            ):
                return ErrorResolution(
                    ResponseAction.FAIL,
                    FailureType.config_error,
                    'A transient authentication error occurred. To prevent future syncs from failing, assign the "Exempt from Transaction Security" user permission to the authenticated user.',
                )

        return ErrorResolution(
            ResponseAction.FAIL,
            FailureType.system_error,
            f"An error occurred: {response.content.decode()}",
        )

    @staticmethod
    def _is_bulk_job_creation(response: requests.Response) -> bool:
        # TODO comment on PR: I don't like that because it duplicates the format of the URL but with a test at least we should be fine to valide once it changes
        return bool(re.compile(r"services/data/[A-Za-z0-9.]+/jobs/query/?$").search(response.url))

    def _handle_bulk_job_creation_endpoint_specific_errors(
        self, response: requests.Response, error_code: Optional[str], error_message: str
    ) -> ErrorResolution:
        # A part of streams can't be used by BULK API. Every API version can have a custom list of
        # these sobjects. Another part of them can be generated dynamically. That's why we can't track
        # them preliminarily and there is only one way is to except error with necessary messages about
        # their limitations. Now we know about 3 different reasons of similar errors:
        # 1) some SaleForce sobjects(streams) is not supported by the BULK API simply (as is).
        # 2) Access to a sobject(stream) is not available
        # 3) sobject is not queryable. It means this sobject can't be called directly.
        #    We can call it as part of response from another sobject only.  E.g.:
        #        initial query: "Select Id, Subject from ActivityHistory" -> error
        #        updated query: "Select Name, (Select Subject,ActivityType from ActivityHistories) from Contact"
        #    The second variant forces customisation for every case (ActivityHistory, ActivityHistories etc).
        #    And the main problem is these subqueries doesn't support CSV response format.
        if error_message == "Selecting compound data not supported in Bulk Query" or (
            error_code == "INVALIDENTITY" and "is not supported by the Bulk API" in error_message
        ):
            logger.error(
                f"Cannot receive data for stream '{self._stream_name}' using BULK API, "
                f"sobject options: {self._sobject_options}, error message: '{error_message}'"
            )
            raise BulkNotSupportedException()
        elif response.status_code == codes.BAD_REQUEST:
            if error_message.endswith("does not support query"):
                logger.error(
                    f"The stream '{self._stream_name}' is not queryable, "
                    f"sobject options: {self._sobject_options}, error message: '{error_message}'"
                )
                raise BulkNotSupportedException()
            elif error_code == "API_ERROR" and error_message.startswith("Implementation restriction"):
                message = f"Unable to sync '{self._stream_name}'. To prevent future syncs from failing, ensure the authenticated user has \"View all Data\" permissions."
                return ErrorResolution(ResponseAction.FAIL, FailureType.config_error, message)
            elif error_code == "LIMIT_EXCEEDED":
                message = "Your API key for Salesforce has reached its limit for the 24-hour period. We will resume replication once the limit has elapsed."
                logger.error(message)
                raise BulkNotSupportedException()
        elif response.status_code == codes.FORBIDDEN:
            if error_code == "REQUEST_LIMIT_EXCEEDED":
                logger.error(
                    f"Cannot receive data for stream '{self._stream_name}' ,"
                    f"sobject options: {self._sobject_options}, Error message: '{error_message}'"
                )
                raise BulkNotSupportedException()
            else:
                logger.error(
                    f"Cannot receive data for stream '{self._stream_name}' ,"
                    f"sobject options: {self._sobject_options}, error message: '{error_message}'"
                )
                raise BulkNotSupportedException()

        return ErrorResolution(ResponseAction.FAIL, FailureType.system_error, error_message)

    @staticmethod
    def _extract_error_code_and_message(response: requests.Response) -> tuple[Optional[str], str]:
        try:
            error_data = response.json()[0]
            return error_data.get("errorCode"), error_data.get("message", "")
        except exceptions.JSONDecodeError:
            logger.warning(f"The response for `{response.request.url}` is not a JSON but was `{response.content}`")
        except (IndexError, KeyError):
            logger.warning(
                f"The response for `{response.request.url}` was expected to be a list with at least one element but was `{response.content}`"
            )

            if "error" in response.json() and "error_description" in response.json():
                return response.json()["error"], response.json()["error_description"]

        return None, f"Unknown error on response `{response.content}`"

    def _is_login_request(self, response: requests.Response) -> bool:
        return "salesforce.com/services/oauth2/token" in response.request.url


def default_backoff_handler(max_tries: int, retry_on=None):
    if not retry_on:
        retry_on = TRANSIENT_EXCEPTIONS
    backoff_method = backoff.constant
    backoff_params = {"interval": 5}

    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying...")

    def should_give_up(exc):
        give_up = (
            SalesforceErrorHandler().interpret_response(exc if exc.response is None else exc.response).response_action
            != ResponseAction.RETRY
        )
        if give_up:
            logger.info(f"Giving up for returned HTTP status: {exc.response.status_code}, body: {exc.response.text}")
        return give_up

    return backoff.on_exception(
        backoff_method,
        retry_on,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=should_give_up,
        max_tries=max_tries,
        **backoff_params,
    )
