#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING

from . import constants


# GitHub's GraphQL error types are not officially documented
# (see https://github.com/github/docs/issues/22607).
# The values below are confirmed via community and third-party client usage.
GRAPHQL_RETRYABLE_TYPES = {"RATE_LIMITED"}
GRAPHQL_CONFIG_ERROR_TYPES = {"FORBIDDEN", "INSUFFICIENT_SCOPES", "MAX_NODE_LIMIT_EXCEEDED"}
GRAPHQL_IGNORE_TYPES = {"NOT_FOUND"}


def classify_graphql_errors(errors: List[Dict[str, Any]]) -> str:
    """Classify a GraphQL `errors[]` array into an action verdict.

    Priority (most-fatal wins):
      1. `CONFIG_ERROR` — FORBIDDEN, INSUFFICIENT_SCOPES, MAX_NODE_LIMIT_EXCEEDED
      2. `RETRY` — RATE_LIMITED, or message containing "timed out" / "exceeded resource limits"
      3. `IGNORE` — NOT_FOUND only (no fatal or retryable types present)
      4. `RETRY` — fallback for unknown types (preserves historical behavior)
    """
    if not errors:
        return "NONE"
    types = {e.get("type") for e in errors if isinstance(e, dict)}
    messages = " ".join(e.get("message", "") for e in errors if isinstance(e, dict)).lower()
    if types & GRAPHQL_CONFIG_ERROR_TYPES:
        return "CONFIG_ERROR"
    if (types & GRAPHQL_RETRYABLE_TYPES) or "timed out" in messages or "exceeded resource limits" in messages:
        return "RETRY"
    known_types = GRAPHQL_CONFIG_ERROR_TYPES | GRAPHQL_RETRYABLE_TYPES | GRAPHQL_IGNORE_TYPES | {None}
    has_unknown = bool(types - known_types)
    if has_unknown:
        return "RETRY"  # unknown error type — preserve historical behavior
    if types & GRAPHQL_IGNORE_TYPES:
        return "IGNORE"
    return "RETRY"  # fallback


def _format_graphql_config_error(stream_name: str, primary: Dict[str, Any], all_errors: List[Dict[str, Any]]) -> str:
    err_type = primary.get("type", "unknown")
    message = primary.get("message", "")
    if err_type == "INSUFFICIENT_SCOPES":
        return f"GitHub GraphQL rejected the `{stream_name}` query: token is missing required scopes. GitHub message: {message!r}"
    if err_type == "FORBIDDEN":
        return (
            f"GitHub GraphQL denied access for the `{stream_name}` query. "
            f"The token may lack permission for the resource, or the organization may require SAML SSO authorization. "
            f"GitHub message: {message!r}"
        )
    if err_type == "MAX_NODE_LIMIT_EXCEEDED":
        return (
            f"GitHub GraphQL refused the `{stream_name}` query: it requests more than 500,000 total nodes. "
            f"Reduce page size or split the query. GitHub message: {message!r}"
        )
    return f"GitHub GraphQL returned a config error ({err_type}) for `{stream_name}`: {message!r}"


GITHUB_DEFAULT_ERROR_MAPPING = DEFAULT_ERROR_MAPPING | {
    401: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.config_error,
        error_message="Conflict.",
    ),
    403: ErrorResolution(
        response_action=ResponseAction.FAIL,
        failure_type=FailureType.config_error,
        error_message="Access denied due to insufficient permissions.",
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
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.config_error,
        error_message="Gone. Please ensure the url is valid.",
    ),
}


def is_conflict_with_empty_repository(response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> bool:
    if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.CONFLICT:
        response_data = response_or_exception.json()
        return response_data.get("message") == "Git Repository is empty."
    return False


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
                return ErrorResolution(
                    response_action=ResponseAction.RATE_LIMITED,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
                )

            if is_conflict_with_empty_repository(response_or_exception=response_or_exception):
                log_message = f"Ignoring response for '{response_or_exception.request.method}' request to '{response_or_exception.url}' with response code '{response_or_exception.status_code}' as the repository is empty."
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
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code in (requests.codes.BAD_GATEWAY, requests.codes.GATEWAY_TIMEOUT):
                self.stream.page_size = max(1, int(self.stream.page_size / 2))
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=(
                        f"GitHub GraphQL returned HTTP {response_or_exception.status_code}. "
                        f"Reducing page size to {self.stream.page_size} and retrying."
                    ),
                )

            self.stream.page_size = (
                constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM if self.stream.large_stream else constants.DEFAULT_PAGE_SIZE
            )

            try:
                body = response_or_exception.json()
            except ValueError:
                body = {}

            errors = body.get("errors") or []
            verdict = classify_graphql_errors(errors)

            if verdict == "CONFIG_ERROR":
                primary = next((e for e in errors if e.get("type") in GRAPHQL_CONFIG_ERROR_TYPES), {})
                return ErrorResolution(
                    response_action=ResponseAction.FAIL,
                    failure_type=FailureType.config_error,
                    error_message=_format_graphql_config_error(self.stream.name, primary, errors),
                )

            if verdict == "IGNORE":
                primary = next((e for e in errors if e.get("type") in GRAPHQL_IGNORE_TYPES), {})
                return ErrorResolution(
                    response_action=ResponseAction.IGNORE,
                    failure_type=FailureType.config_error,
                    error_message=(
                        f"Skipping `{self.stream.name}` page: GitHub GraphQL returned NOT_FOUND "
                        f"for path {primary.get('path')}. Message: {primary.get('message', '')!r}"
                    ),
                )

            if verdict == "RETRY":
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=(f"GitHub GraphQL returned errors. Retrying. First error: {errors[0] if errors else 'n/a'}"),
                )

        return super().interpret_response(response_or_exception)
