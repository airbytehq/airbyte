#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from dataclasses import dataclass
from itertools import cycle
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import pendulum
import requests
from airbyte_cdk import BackoffStrategy
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from airbyte_protocol.models import FailureType

from . import constants


def getter(D: Dict[str, Any], key_or_keys: Union[List[Any], Any], strict: bool = True) -> Dict[str, Any]:
    if not isinstance(key_or_keys, list):
        key_or_keys = [key_or_keys]
    for k in key_or_keys:
        if strict:
            D = D[k]
        else:
            D = D.get(k, {})
    return D


def read_full_refresh(stream_instance: Stream) -> Iterable[Mapping[str, Any]]:
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        records = stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            yield record


class GitHubAPILimitException(Exception):
    """General class for Rate Limits errors"""


@dataclass
class Token:
    count_rest: int = 5000
    count_graphql: int = 5000
    reset_at_rest: pendulum.DateTime = pendulum.now()
    reset_at_graphql: pendulum.DateTime = pendulum.now()


class MultipleTokenAuthenticatorWithRateLimiter(AbstractHeaderAuthenticator):
    """
    Each token in the cycle is checked against the rate limiter.
    If a token exceeds the capacity limit, the system switches to another token.
    If all tokens are exhausted, the system will enter a sleep state until
    the first token becomes available again.
    """

    DURATION = pendulum.duration(seconds=3600)  # Duration at which the current rate limit window resets

    def __init__(self, tokens: List[str], auth_method: str = "token", auth_header: str = "Authorization"):
        self._auth_method = auth_method
        self._auth_header = auth_header
        self._tokens = {t: Token() for t in tokens}
        self.check_all_tokens()
        self._tokens_iter = cycle(self._tokens)
        self._active_token = next(self._tokens_iter)
        self._max_time = 60 * 10  # 10 minutes as default

    @property
    def auth_header(self) -> str:
        return self._auth_header

    def get_auth_header(self) -> Mapping[str, Any]:
        """The header to set on outgoing HTTP requests"""
        if self.auth_header:
            return {self.auth_header: self.token}
        return {}

    def __call__(self, request: Any) -> Any:
        """Attach the HTTP headers required to authenticate on the HTTP request"""
        while True:
            current_token = self._tokens[self.current_active_token]
            if "graphql" in request.path_url:
                if self.process_token(current_token, "count_graphql", "reset_at_graphql"):
                    break
            else:
                if self.process_token(current_token, "count_rest", "reset_at_rest"):
                    break

        request.headers.update(self.get_auth_header())

        return request

    @property
    def current_active_token(self) -> str:
        return self._active_token

    def update_token(self) -> None:
        self._active_token = next(self._tokens_iter)

    @property
    def token(self) -> str:

        token = self.current_active_token
        return f"{self._auth_method} {token}"

    @property
    def max_time(self) -> int:
        return self._max_time

    @max_time.setter
    def max_time(self, value: int) -> None:
        self._max_time = value

    def _check_token_limits(self, token: str) -> None:
        """check that token is not limited"""
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        rate_limit_info = (
            requests.get(
                "https://api.github.com/rate_limit", headers=headers, auth=TokenAuthenticator(token, auth_method=self._auth_method)
            )
            .json()
            .get("resources")
        )
        token_info = self._tokens[token]
        remaining_info_core = rate_limit_info.get("core")
        token_info.count_rest, token_info.reset_at_rest = remaining_info_core.get("remaining"), pendulum.from_timestamp(
            remaining_info_core.get("reset")
        )

        remaining_info_graphql = rate_limit_info.get("graphql")
        token_info.count_graphql, token_info.reset_at_graphql = remaining_info_graphql.get("remaining"), pendulum.from_timestamp(
            remaining_info_graphql.get("reset")
        )

    def check_all_tokens(self) -> None:
        for token in self._tokens:
            self._check_token_limits(token)

    def process_token(self, current_token: Any, count_attr: str, reset_attr: str) -> bool:
        if getattr(current_token, count_attr) > 0:
            setattr(current_token, count_attr, getattr(current_token, count_attr) - 1)
            return True
        elif all(getattr(x, count_attr) == 0 for x in self._tokens.values()):
            min_time_to_wait = min((getattr(x, reset_attr) - pendulum.now()).in_seconds() for x in self._tokens.values())
            if min_time_to_wait < self.max_time:
                time.sleep(min_time_to_wait if min_time_to_wait > 0 else 0)
                self.check_all_tokens()
            else:
                raise GitHubAPILimitException(f"Rate limits for all tokens ({count_attr}) were reached")
        else:
            self.update_token()
        return False


GITHUB_DEFAULT_ERROR_MAPPING = DEFAULT_ERROR_MAPPING | {
    401: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.config_error,
        error_message="Conflict.",
    ),
    403: ErrorResolution(
        response_action=ResponseAction.RETRY,
        failure_type=FailureType.config_error,
        error_message="Conflict.",
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
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",  # type: ignore[union-attr]
                )

        return super().interpret_response(response_or_exception)


class ContributorActivityErrorHandler(HttpStatusErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.ACCEPTED:
            return ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.transient_error,
                error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",  # type: ignore[union-attr]
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
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",  # type: ignore[union-attr]
                )

            self.stream.page_size = (
                constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM if self.stream.large_stream else constants.DEFAULT_PAGE_SIZE
            )

            if response_or_exception.json().get("errors"):
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",  # type: ignore[union-attr]
                )

        return super().interpret_response(response_or_exception)


class GithubStreamABCBackoffStrategy(BackoffStrategy):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        # This method is called if we run into the rate limit. GitHub limits requests to 5000 per hour and provides
        # `X-RateLimit-Reset` header which contains time when this hour will be finished and limits will be reset so
        # we again could have 5000 per another hour.
        if isinstance(response_or_exception, requests.Response):
            min_backoff_time = 60.0
            retry_after = response_or_exception.headers.get("Retry-After")
            if retry_after is not None:
                backoff_time_in_seconds = max(float(retry_after), min_backoff_time)
                return self.get_waiting_time(backoff_time_in_seconds)

            reset_time = response_or_exception.headers.get("X-RateLimit-Reset")
            if reset_time:
                backoff_time_in_seconds = max(float(reset_time) - time.time(), min_backoff_time)
                return self.get_waiting_time(backoff_time_in_seconds)
        return None

    def get_waiting_time(self, backoff_time_in_seconds: Optional[float]) -> Optional[float]:
        if backoff_time_in_seconds < 60 * 10:  # type: ignore[operator]
            return backoff_time_in_seconds
        else:
            self.stream._http_client._session.auth.update_token()  # New token will be used in next request
            return 1


class ContributorActivityBackoffStrategy(BackoffStrategy):
    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.ACCEPTED:
            return 90
        return None
