#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from itertools import cycle
from typing import Any, List, Mapping

import requests

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now, ab_datetime_parse


def getter(D: dict, key_or_keys, strict=True):
    if not isinstance(key_or_keys, list):
        key_or_keys = [key_or_keys]
    for k in key_or_keys:
        if strict:
            D = D[k]
        else:
            D = D.get(k, {})
    return D


def read_full_refresh(stream_instance: Stream):
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
    reset_at_rest: AirbyteDateTime = ab_datetime_now()
    reset_at_graphql: AirbyteDateTime = ab_datetime_now()


class MultipleTokenAuthenticatorWithRateLimiter(AbstractHeaderAuthenticator):
    """
    Each token in the cycle is checked against the rate limiter.
    If a token exceeds the capacity limit, the system switches to another token.
    If all tokens are exhausted, the system will enter a sleep state until
    the first token becomes available again.

    An API budget mechanism throttles requests proactively: when a token's
    remaining quota drops below a configurable reserve, a small delay is
    injected before the request so that the connector never fully exhausts
    all tokens at once.
    """

    DURATION = timedelta(seconds=3600)  # Duration at which the current rate limit window resets
    BUDGET_RESERVE_FRACTION = 0.1  # Start throttling when only 10% of quota remains
    BUDGET_MIN_RESERVE = 50  # Always keep at least this many calls in reserve per token

    def __init__(self, tokens: List[str], auth_method: str = "token", auth_header: str = "Authorization"):
        self._logger = logging.getLogger("airbyte")
        self._auth_method = auth_method
        self._auth_header = auth_header
        self._tokens = {t: Token() for t in tokens}
        # It would've been nice to instantiate a single client on this authenticator. However, we are checking
        # the limits of each token which is associated with a TokenAuthenticator. And each HttpClient can only
        # correspond to one authenticator.
        self._token_to_http_client: Mapping[str, HttpClient] = self._initialize_http_clients(tokens)
        self.check_all_tokens()
        self._tokens_iter = cycle(self._tokens)
        self._active_token = next(self._tokens_iter)
        self._max_time = 60 * 10  # 10 minutes as default
        self._budget_logged = False  # avoid log spam for throttle messages

    def _initialize_http_clients(self, tokens: List[str]) -> Mapping[str, HttpClient]:
        return {
            token: HttpClient(
                name="token_validator",
                logger=self._logger,
                authenticator=TokenAuthenticator(token, auth_method=self._auth_method),
                use_cache=False,  # We don't want to reuse cached valued because rate limit values change frequently
            )
            for token in tokens
        }

    @property
    def auth_header(self) -> str:
        return self._auth_header

    def get_auth_header(self) -> Mapping[str, Any]:
        """The header to set on outgoing HTTP requests"""
        if self.auth_header:
            return {self.auth_header: self.token}
        return {}

    def __call__(self, request):
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

    def _check_token_limits(self, token: str):
        """check that token is not limited"""

        http_client = self._token_to_http_client.get(token)
        if not http_client:
            raise ValueError("No HttpClient was initialized for this token. This is unexpected. Please contact Airbyte support.")

        _, response = http_client.send_request(
            http_method="GET",
            url="https://api.github.com/rate_limit",
            headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
            request_kwargs={},
        )

        response_body = response.json()
        if "resources" not in response_body:
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                internal_message=f"Token rate limit info response did not contain expected key: resources",
                message="Unable to validate token. Please double check that specified authentication tokens are correct",
            )

        rate_limit_info = response_body.get("resources")
        token_info = self._tokens[token]
        remaining_info_core = rate_limit_info.get("core")
        token_info.count_rest, token_info.reset_at_rest = (
            remaining_info_core.get("remaining"),
            ab_datetime_parse(remaining_info_core.get("reset")),
        )

        remaining_info_graphql = rate_limit_info.get("graphql")
        token_info.count_graphql, token_info.reset_at_graphql = (
            remaining_info_graphql.get("remaining"),
            ab_datetime_parse(remaining_info_graphql.get("reset")),
        )

    def check_all_tokens(self):
        for token in self._tokens:
            self._check_token_limits(token)
        self._budget_logged = False

    def _get_budget_reserve(self, token: Token, count_attr: str) -> int:
        """Return the minimum number of calls to keep in reserve for a token.

        The reserve is the larger of ``BUDGET_MIN_RESERVE`` and
        ``BUDGET_RESERVE_FRACTION`` of the token's actual remaining count.
        We use the current remaining value as an approximation when the
        original limit is unknown.
        """
        remaining = getattr(token, count_attr)
        # Use 5000 (GitHub default) as the basis, but fall back to the
        # remaining count if it's higher (e.g. enterprise tokens).
        limit_estimate = max(5000, remaining)
        return max(self.BUDGET_MIN_RESERVE, int(limit_estimate * self.BUDGET_RESERVE_FRACTION))

    def _apply_budget_throttle(self, token: Token, count_attr: str, reset_attr: str) -> None:
        """Optionally sleep a little to spread remaining calls over the reset window.

        When the remaining count for *all* tokens is below the budget
        reserve, we inject a short delay proportional to how much time
        remains until the rate-limit window resets.  This avoids hitting
        the wall and having to do a long blocking sleep.
        """
        reserve = self._get_budget_reserve(token, count_attr)
        remaining = getattr(token, count_attr)
        if remaining > reserve:
            return  # plenty of headroom — no throttling needed

        # Only throttle when *every* token is running low so that we don't
        # slow down needlessly while other tokens still have capacity.
        if not all(getattr(t, count_attr) <= self._get_budget_reserve(t, count_attr) for t in self._tokens.values()):
            return

        # Calculate a proportional delay: spread the remaining calls evenly
        # across the time left until the earliest reset.
        seconds_to_reset = max((getattr(token, reset_attr) - ab_datetime_now()).total_seconds(), 0)
        total_remaining = sum(max(getattr(t, count_attr), 0) for t in self._tokens.values())
        if total_remaining <= 0 or seconds_to_reset <= 0:
            return

        delay = seconds_to_reset / total_remaining
        # Cap the delay to avoid extremely long pauses on single requests
        delay = min(delay, 10.0)
        if delay >= 0.1:
            if not self._budget_logged:
                self._logger.info(
                    "API budget: throttling requests (%.1fs delay). %d calls remaining across %d token(s), " "%.0fs until reset.",
                    delay,
                    total_remaining,
                    len(self._tokens),
                    seconds_to_reset,
                )
                self._budget_logged = True
            time.sleep(delay)

    HEARTBEAT_INTERVAL = 60.0  # Log every 60s during exhaustion sleep

    def _sleep_with_heartbeat(self, total_seconds: float, count_attr: str) -> None:
        """Sleep for *total_seconds* but log progress periodically so the
        platform heartbeat stays alive and operators can see the connector
        is not stuck."""
        remaining = total_seconds
        while remaining > 0:
            chunk = min(remaining, self.HEARTBEAT_INTERVAL)
            time.sleep(chunk)
            remaining -= chunk
            if remaining > 0:
                self._logger.info(
                    "Rate limit exhausted (%s). Waiting for reset — %.0fs remaining.",
                    count_attr,
                    remaining,
                )

    def process_token(self, current_token, count_attr, reset_attr):
        if getattr(current_token, count_attr) > 0:
            self._apply_budget_throttle(current_token, count_attr, reset_attr)
            setattr(current_token, count_attr, getattr(current_token, count_attr) - 1)
            return True
        elif all(getattr(x, count_attr) == 0 for x in self._tokens.values()):
            min_time_to_wait = min((getattr(x, reset_attr) - ab_datetime_now()).total_seconds() for x in self._tokens.values())
            if min_time_to_wait < self.max_time:
                self._logger.info(
                    "All tokens exhausted (%s). Sleeping %.0fs until rate limit resets.",
                    count_attr,
                    max(min_time_to_wait, 0),
                )
                self._sleep_with_heartbeat(max(min_time_to_wait, 0), count_attr)
                self.check_all_tokens()
            else:
                raise GitHubAPILimitException(f"Rate limits for all tokens ({count_attr}) were reached")
        else:
            self.update_token()
        return False
