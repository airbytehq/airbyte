#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Protocol, Union
from urllib.parse import urlparse

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING

from . import constants


logger = logging.getLogger("airbyte")


class GithubStreamProtocol(Protocol):
    name: str
    requires_repo_admin_access: bool


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


def is_stargazers_access_restriction(response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> bool:
    if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.FORBIDDEN:
        try:
            response_data = response_or_exception.json()
        except ValueError:
            logger.warning(
                "is_stargazers_access_restriction received non-JSON 403 response (first 50 chars: %r).",
                response_or_exception.text[:50],
            )
            return False
        documentation_url = response_data.get("documentation_url") if isinstance(response_data, dict) else None
        if not isinstance(documentation_url, str):
            return False
        documentation_url = documentation_url.lower()
        return "/rest/activity/starring" in documentation_url or "/rest/activity/watching" in documentation_url
    return False


class GithubStreamABCErrorHandler(HttpStatusErrorHandler):
    def __init__(self, stream: GithubStreamProtocol, **kwargs):
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

            status_code = response_or_exception.status_code
            if self.stream.requires_repo_admin_access and (
                status_code == requests.codes.NOT_FOUND
                or (status_code == requests.codes.FORBIDDEN and is_stargazers_access_restriction(response_or_exception))
            ):
                response_url = response_or_exception.url
                path_parts = urlparse(response_url).path.strip("/").split("/") if isinstance(response_url, str) else []
                repos_index = path_parts.index("repos") if "repos" in path_parts else -1
                repository = (
                    "/".join(path_parts[repos_index + 1 : repos_index + 3])
                    if repos_index >= 0 and len(path_parts) >= repos_index + 3
                    else ""
                )
                repository_label = f" for repository `{repository}`" if repository else ""
                deleted_repository_message = (
                    "; a deleted or renamed repository would also return HTTP 404." if status_code == requests.codes.NOT_FOUND else "."
                )
                error_message = (
                    f"Skipping `{self.stream.name}`{repository_label}: GitHub returned HTTP "
                    f"{status_code} for this endpoint. Since June 30, 2026, GitHub "
                    f"restricts the stargazers/watchers listing endpoints to repository admins and "
                    f"collaborators, which is the most likely cause when the configured token neither "
                    f"administers nor collaborates on the repository{deleted_repository_message} This stream "
                    f"will emit no records when the token lacks that access. "
                    f"Only aggregate star counts remain available through GraphQL, which this connector does "
                    f"not currently expose. See "
                    f"https://github.blog/changelog/2026-06-30-upcoming-access-restrictions-to-public-api-endpoints-and-ui-views/"
                )
                self._logger.warning(error_message)
                return ErrorResolution(
                    response_action=ResponseAction.IGNORE,
                    failure_type=FailureType.config_error,
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
                # Halve the page size on every 502/504 to reduce GraphQL query cost,
                # but never let it drop below 1 — a page_size of 0 would request no
                # records and cause infinite paging.
                previous_page_size = self.stream.page_size
                self.stream.page_size = max(1, int(self.stream.page_size / 2))
                self._logger.info(
                    "GitHub GraphQL endpoint returned HTTP %s for stream `%s`; reducing GraphQL page_size from %s to %s and retrying.",
                    response_or_exception.status_code,
                    self.stream.name,
                    previous_page_size,
                    self.stream.page_size,
                )
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=(
                        f"GitHub GraphQL endpoint returned HTTP {response_or_exception.status_code} "
                        f"for stream `{self.stream.name}`. Reducing GraphQL page size and retrying."
                    ),
                )

            self.stream.page_size = (
                constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM if self.stream.large_stream else constants.DEFAULT_PAGE_SIZE
            )

            if self._safe_json_get_errors(response_or_exception):
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=(
                        f"GitHub GraphQL endpoint returned errors in the response body "
                        f"for stream `{self.stream.name}` (HTTP {response_or_exception.status_code}). Retrying."
                    ),
                )

        return super().interpret_response(response_or_exception)
