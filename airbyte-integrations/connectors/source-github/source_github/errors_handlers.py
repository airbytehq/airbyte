#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Dict, Optional, Union

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


def parse_sso_header(headers: Dict[str, Any]) -> Optional[Dict[str, Optional[str]]]:
    """Parse the X-GitHub-SSO response header.

    GitHub sends this header when a token lacks SAML SSO authorization.
    Format examples:
      required; url=https://github.com/orgs/ORG/sso?authorization_request=XXXXX
      partial-results; organizations=ORG1,ORG2
    """
    sso_value = headers.get("X-GitHub-SSO")
    if not sso_value:
        return None

    result: Dict[str, Optional[str]] = {"state": None, "url": None, "organizations": None}
    parts = [p.strip() for p in sso_value.split(";")]
    if parts:
        result["state"] = parts[0]
    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key == "url":
                result["url"] = value
            elif key == "organizations":
                result["organizations"] = value
    return result


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
            # SSO authorization check — must run before rate-limit handling
            if response_or_exception.status_code in (requests.codes.FORBIDDEN, requests.codes.NOT_FOUND):
                sso_info = parse_sso_header(response_or_exception.headers)
                if sso_info and sso_info.get("state") == "required":
                    authorize_url = sso_info.get("url", "")
                    error_message = (
                        f"GitHub SAML SSO authorization is required. "
                        f"The access token is not authorized for the requested organization. "
                        f"Authorize this token at: {authorize_url}"
                    )
                    return ErrorResolution(
                        response_action=ResponseAction.FAIL,
                        failure_type=FailureType.config_error,
                        error_message=error_message,
                    )
            elif response_or_exception.status_code == requests.codes.OK:
                sso_info = parse_sso_header(response_or_exception.headers)
                if sso_info and sso_info.get("state") == "partial-results":
                    orgs = sso_info.get("organizations", "")
                    logger.warning(
                        f"GitHub SAML SSO partial results returned for stream `{self.stream.name}`. "
                        f"Some organization data may be missing. Affected organizations: {orgs}"
                    )

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
                self.stream.page_size = int(self.stream.page_size / 2)
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
                )

            self.stream.page_size = (
                constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM if self.stream.large_stream else constants.DEFAULT_PAGE_SIZE
            )

            if response_or_exception.json().get("errors"):
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
                )

        return super().interpret_response(response_or_exception)
