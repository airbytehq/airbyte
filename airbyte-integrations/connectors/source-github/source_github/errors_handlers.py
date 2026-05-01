#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets

from . import constants


GITHUB_DEFAULT_ERROR_MAPPING = DEFAULT_ERROR_MAPPING | {
    401: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message="GitHub authentication failed. Token is invalid or expired.",
    ),
    # TODO(M1): detect X-GitHub-SSO header and surface the SAML authorize URL.
    403: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message=(
            "GitHub denied access (HTTP 403). Your token may be missing required scopes "
            "(this connector typically needs: repo, read:org, read:user, read:project, workflow), "
            "or this organization may require SAML SSO authorization."
        ),
    ),
    404: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message=(
            "GitHub returned 404. The resource does not exist or the token lacks access. "
            "GitHub may return 404 instead of 403 for inaccessible resources."
        ),
    ),
    409: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.transient_error,
        error_message="GitHub API returned a conflict. The repository may be empty or temporarily unavailable.",
    ),
    410: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message="GitHub resource is gone or unavailable for this endpoint.",
    ),
}


def is_conflict_with_empty_repository(response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> bool:
    if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.CONFLICT:
        response_data = response_or_exception.json()
        return response_data.get("message") == "Git Repository is empty."
    return False


def _rate_limit_message(response: requests.Response) -> str:
    prefix = "GitHub API rate limit exceeded."
    if retry_after := response.headers.get("Retry-After"):
        return f"{prefix} Retry after {retry_after} seconds."
    if reset_at := response.headers.get("X-RateLimit-Reset"):
        return f"{prefix} Rate limit resets at epoch {reset_at}."
    return prefix


def _format_github_validation_error(response: requests.Response) -> str:
    try:
        body = response.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        return "GitHub API validation failed."

    message = body.get("message") or "GitHub API validation failed."
    errors = body.get("errors") or []
    details = []
    for error in errors:
        if isinstance(error, dict):
            parts = [str(error.get(key)) for key in ("resource", "field", "code", "message") if error.get(key)]
            if parts:
                details.append(" / ".join(parts))

    if details:
        return f"{message}: {'; '.join(details)}"
    return message


class GithubStreamABCErrorHandler(HttpStatusErrorHandler):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            retry_flag = (
                # The GitHub GraphQL API has limitations
                # https://docs.github.com/en/graphql/overview/resource-limitations
                (
                    response_or_exception.headers.get("X-RateLimit-Resource") == "graphql"
                    and self.stream.check_graphql_rate_limited(response_or_exception.json())
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

                status_code = response_or_exception.status_code
                error_message = (
                    f"GitHub rate limit hit for stream '{self.stream.name}' (HTTP {status_code}). "
                    f"Waiting for the rate limit window to reset before retrying."
                )

                return ErrorResolution(
                    response_action=ResponseAction.RATE_LIMITED,
                    failure_type=FailureType.transient_error,
                    error_message=error_message,
                )

            if response_or_exception.status_code == requests.codes.UNPROCESSABLE_ENTITY:
                return ErrorResolution(
                    response_action=ResponseAction.FAIL,
                    failure_type=FailureType.config_error,
                    error_message=_format_github_validation_error(response_or_exception),
                )

            if is_conflict_with_empty_repository(response_or_exception=response_or_exception):
                log_message = (
                    f"Skipping '{self.stream.name}' for this repository: GitHub returned 409 Conflict "
                    f"with message 'Git Repository is empty.' This means the repository has no commits."
                )
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
                error_message="GitHub is computing repository statistics. Retrying.",
            )

        return super().interpret_response(response_or_exception)


class GitHubGraphQLErrorHandler(GithubStreamABCErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            # GraphQL rate-limit responses (HTTP 200 with errors[].type == "RATE_LIMITED")
            # must be classified before the generic errors branch, otherwise they are
            # misclassified as retryable GraphQL errors.
            if response_or_exception.headers.get("X-RateLimit-Resource") == "graphql" and self.stream.check_graphql_rate_limited(
                response_or_exception.json()
            ):
                return super().interpret_response(response_or_exception)

            if response_or_exception.status_code in (requests.codes.BAD_GATEWAY, requests.codes.GATEWAY_TIMEOUT):
                self.stream.page_size = int(self.stream.page_size / 2)
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"GitHub API gateway timeout for stream `{self.stream.name}`. Reducing page size and retrying.",
                )

            self.stream.page_size = (
                constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM if self.stream.large_stream else constants.DEFAULT_PAGE_SIZE
            )

            if response_or_exception.json().get("errors"):
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"GitHub GraphQL API returned errors for stream `{self.stream.name}`. Retrying.",
                )

        return super().interpret_response(response_or_exception)
