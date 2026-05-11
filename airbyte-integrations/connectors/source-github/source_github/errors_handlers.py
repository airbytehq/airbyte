#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING

from . import constants


logger = logging.getLogger("airbyte")


GITHUB_DEFAULT_ERROR_MAPPING = DEFAULT_ERROR_MAPPING | {
    401: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.config_error,
        error_message="Conflict.",
    ),
    403: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message=(
            "GitHub denied access (HTTP 403). Your token may be missing required scopes "
            "(this connector typically needs: repo, read:org, read:user, read:project, workflow), "
            "or this organization may require SAML SSO authorization. "
            "See https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api"
        ),
    ),
    404: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.config_error,
        error_message="Conflict.",
    ),
    409: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.config_error,
        error_message="Conflict.",
    ),
    410: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message=(
            "GitHub returned 410 Gone for an unexpected reason. "
            "The endpoint or API version may be deprecated. "
            "Verify the connector version is current and the endpoint is still supported."
        ),
    ),
}


def is_conflict_with_empty_repository(response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> bool:
    if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.CONFLICT:
        try:
            response_data = response_or_exception.json()
        except ValueError:
            logger.warning(
                "is_conflict_with_empty_repository received non-JSON 409 response (first 50 chars: %r).",
                response_or_exception.text[:50],
            )
            return False
        return response_data.get("message") == "Git Repository is empty."
    return False


def is_gone_with_feature_disabled(response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> bool:
    if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.GONE:
        try:
            message = (response_or_exception.json().get("message") or "").lower()
        except ValueError:
            logger.warning(
                "is_gone_with_feature_disabled received non-JSON 410 response (first 50 chars: %r).",
                response_or_exception.text[:50],
            )
            return False
        return "are disabled" in message or "is disabled" in message
    return False


class GithubStreamABCErrorHandler(HttpStatusErrorHandler):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def _safe_json_check_graphql_rate_limited(self, response: requests.Response) -> bool:
        try:
            body = response.json()
        except ValueError:
            self._logger.warning(
                "GraphQL rate-limit check received non-JSON response (HTTP %s, first 50 chars: %r).",
                response.status_code,
                response.text[:50],
            )
            return False
        return self.stream.check_graphql_rate_limited(body or {})

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            retry_flag = (
                # The GitHub GraphQL API has limitations
                # https://docs.github.com/en/graphql/overview/resource-limitations
                (
                    response_or_exception.headers.get("X-RateLimit-Resource") == "graphql"
                    and self._safe_json_check_graphql_rate_limited(response_or_exception)
                )
                # Rate limit HTTP headers
                # https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limit-http-headers
                or (response_or_exception.status_code != 200 and response_or_exception.headers.get("X-RateLimit-Remaining") == "0")
                # Secondary rate limits
                # https://docs.github.com/en/rest/overview/resources-in-the-rest-api#secondary-rate-limits
                or "Retry-After" in response_or_exception.headers
            )
            if retry_flag:
                headers = [
                    "X-RateLimit-Resource",
                    "X-RateLimit-Remaining",
                    "X-RateLimit-Reset",
                    "X-RateLimit-Limit",
                    "X-RateLimit-Used",
                    "Retry-After",
                ]
                string_headers = ", ".join(
                    [f"{h}: {response_or_exception.headers[h]}" for h in headers if h in response_or_exception.headers]
                )
                if string_headers:
                    string_headers = f"HTTP headers: {string_headers},"

                self._logger.info(
                    f"Rate limit handling for stream `{self.stream.name}` for the response with {response_or_exception.status_code} status code, {string_headers} with message: {response_or_exception.text}"
                )
                return ErrorResolution(
                    response_action=ResponseAction.RATE_LIMITED,
                    failure_type=FailureType.transient_error,
                    error_message=(
                        f"GitHub rate limit hit for stream `{self.stream.name}` "
                        f"(HTTP {response_or_exception.status_code}). "
                        f"Waiting for the rate limit window to reset before retrying."
                    ),
                )

            if is_conflict_with_empty_repository(response_or_exception=response_or_exception):
                log_message = (
                    f"Skipping `{self.stream.name}` for this repository: GitHub returned 409 Conflict "
                    f"with message 'Git Repository is empty.' This means the repository has no commits."
                )
                return ErrorResolution(
                    response_action=ResponseAction.IGNORE,
                    failure_type=FailureType.config_error,
                    error_message=log_message,
                )

            if is_gone_with_feature_disabled(response_or_exception=response_or_exception):
                log_message = f"Skipping stream slice for '{response_or_exception.url}': {response_or_exception.json().get('message', 'Feature disabled')}."
                return ErrorResolution(
                    response_action=ResponseAction.IGNORE,
                    failure_type=FailureType.config_error,
                    error_message=log_message,
                )

        return super().interpret_response(response_or_exception)


class ContributorActivityErrorHandler(GithubStreamABCErrorHandler):
    """
    This custom error handler is needed for streams based on repository statistics endpoints like ContributorActivity because
    when requesting data that hasn't been cached yet when the request is made, you'll receive a 202 response. And these requests
    need to retried to get the actual results.

    See the docs for more info:
    https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28#a-word-about-caching
    """

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.ACCEPTED:
            return ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.transient_error,
                error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
            )

        return super().interpret_response(response_or_exception)


class GitHubGraphQLErrorHandler(GithubStreamABCErrorHandler):
    def _safe_json_get_errors(self, response: requests.Response) -> bool:
        try:
            body = response.json()
        except ValueError:
            return False
        return bool((body or {}).get("errors"))

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code in (requests.codes.BAD_GATEWAY, requests.codes.GATEWAY_TIMEOUT):
                self.stream.page_size = int(self.stream.page_size / 2)
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
                )

            self.stream.page_size = (
                constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM if self.stream.large_stream else constants.DEFAULT_PAGE_SIZE
            )

            if self._safe_json_get_errors(response_or_exception):
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
                )

        return super().interpret_response(response_or_exception)
