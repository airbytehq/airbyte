#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from itertools import cycle
from typing import Any, Dict, List, Mapping, Optional, Tuple

import backoff
import jwt
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
    """

    DURATION = timedelta(seconds=3600)  # Duration at which the current rate limit window resets

    REFRESH_BUFFER_SECONDS = 300  # Refresh token 5 minutes before expiry

    def __init__(self, tokens: List[str], auth_method: str = "token", auth_header: str = "Authorization", api_url: str = "https://api.github.com", github_app_config: Optional[Dict[str, str]] = None):
        self._logger = logging.getLogger("airbyte")
        self._auth_method = auth_method
        self._auth_header = auth_header
        self._api_url = api_url.rstrip("/")
        self._github_app_config = github_app_config
        self._token_expires_at: Optional[float] = time.time() + 3600 if github_app_config else None
        self._tokens = {t: Token() for t in tokens}
        # It would've been nice to instantiate a single client on this authenticator. However, we are checking
        # the limits of each token which is associated with a TokenAuthenticator. And each HttpClient can only
        # correspond to one authenticator.
        self._token_to_http_client: Mapping[str, HttpClient] = self._initialize_http_clients(tokens)
        self.check_all_tokens()
        self._tokens_iter = cycle(self._tokens)
        self._active_token = next(self._tokens_iter)
        self._max_time = 60 * 10  # 10 minutes as default

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

    def _refresh_token_if_needed(self):
        """Refresh the GitHub App installation token if it's close to expiry.

        Note: this method is called per-request from __call__(). Airbyte's source
        framework is single-threaded for HTTP calls, so no locking is needed.
        """
        if self._github_app_config is None:
            return
        if time.time() < self._token_expires_at - self.REFRESH_BUFFER_SECONDS:
            return

        self._logger.info("GitHub App installation token is expiring soon, refreshing...")
        # GitHub App auth always uses a single token
        assert len(self._tokens) == 1, "GitHub App auth only supports a single token"
        old_token = list(self._tokens.keys())[0]
        new_token, expires_at = generate_github_app_token(**self._github_app_config)

        # Replace the token in all internal data structures
        token_state = self._tokens.pop(old_token)
        self._tokens[new_token] = token_state
        self._token_to_http_client.pop(old_token)
        self._token_to_http_client.update(self._initialize_http_clients([new_token]))
        self._tokens_iter = cycle(self._tokens)
        self._active_token = next(self._tokens_iter)
        self._token_expires_at = self._parse_expiry(expires_at)

        self._logger.info("GitHub App installation token refreshed successfully")

    @staticmethod
    def _parse_expiry(expires_at: Optional[str]) -> float:
        """Parse the expires_at ISO 8601 timestamp from GitHub, falling back to 1 hour from now."""
        if expires_at:
            try:
                from datetime import datetime, timezone
                return datetime.fromisoformat(expires_at.replace("Z", "+00:00")).timestamp()
            except (ValueError, TypeError):
                pass
        return time.time() + 3600

    def __call__(self, request):
        """Attach the HTTP headers required to authenticate on the HTTP request"""
        self._refresh_token_if_needed()
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
            url=f"{self._api_url}/rate_limit",
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

    def process_token(self, current_token, count_attr, reset_attr):
        if getattr(current_token, count_attr) > 0:
            setattr(current_token, count_attr, getattr(current_token, count_attr) - 1)
            return True
        elif all(getattr(x, count_attr) == 0 for x in self._tokens.values()):
            min_time_to_wait = min((getattr(x, reset_attr) - ab_datetime_now()).total_seconds() for x in self._tokens.values())
            if min_time_to_wait < self.max_time:
                time.sleep(min_time_to_wait if min_time_to_wait > 0 else 0)
                self.check_all_tokens()
            else:
                raise GitHubAPILimitException(f"Rate limits for all tokens ({count_attr}) were reached")
        else:
            self.update_token()
        return False


def generate_github_app_token(app_id: str, private_key: str, installation_id: str, api_url: str = "https://api.github.com") -> Tuple[str, Optional[str]]:
    """Generate a GitHub App installation access token.

    Creates a JWT signed with the app's private key, then exchanges it for
    a short-lived installation access token (expires in 1 hour).

    Returns a tuple of (token, expires_at) where expires_at is an ISO 8601
    timestamp string from the GitHub API response, or None if not present.
    """
    logger = logging.getLogger("airbyte")

    # PEM keys pasted through UI forms often have literal "\n" instead of
    # real newlines, which causes PyJWT to fail with a confusing
    # "Could not parse the provided public key" error.
    private_key = private_key.replace("\\n", "\n").strip()

    now = int(time.time())
    payload = {
        "iat": now - 60,  # issued at (60s in the past for clock skew)
        "exp": now + (10 * 60),  # expires in 10 minutes (max allowed)
        "iss": app_id,
    }
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    api_url = api_url.rstrip("/")
    url = f"{api_url}/app/installations/{installation_id}/access_tokens"
    logger.info(f"Requesting GitHub App installation token from {url}")

    try:
        response = _post_with_retry(url, encoded_jwt)
    except requests.exceptions.RequestException as e:
        raise AirbyteTracedException(
            message="Failed to generate GitHub App installation token after retries. "
                    "Check network connectivity and GitHub API status.",
            internal_message=str(e),
            failure_type=FailureType.transient_error,
        )

    if response.status_code != 201:
        raise AirbyteTracedException(
            message=f"Failed to generate GitHub App installation token (HTTP {response.status_code}). "
                    "Verify your App ID, Installation ID, and private key are correct.",
            internal_message=f"GitHub App token exchange failed: {response.text}",
            failure_type=FailureType.config_error,
        )

    data = response.json()
    token = data["token"]
    expires_at = data.get("expires_at")
    logger.info(f"Successfully generated GitHub App installation token (expires_at={expires_at})")
    return token, expires_at


def _should_retry(e):
    """Retry on network errors and 5xx/429 responses."""
    if isinstance(e, requests.exceptions.RequestException) and not isinstance(e, requests.exceptions.HTTPError):
        return True
    if hasattr(e, "response") and e.response is not None:
        return e.response.status_code == 429 or e.response.status_code >= 500
    return False


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=4, giveup=lambda e: not _should_retry(e))
def _post_with_retry(url: str, bearer_token: str) -> requests.Response:
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {bearer_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=30,
    )
    if response.status_code == 429 or response.status_code >= 500:
        raise requests.exceptions.HTTPError(response=response)
    return response
