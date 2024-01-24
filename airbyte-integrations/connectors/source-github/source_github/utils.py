#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from dataclasses import dataclass
from itertools import cycle
from typing import List

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType


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


@dataclass
class Token:
    count: int
    update_at: pendulum.DateTime
    reset_at: pendulum.DateTime


class MultipleTokenAuthenticatorWithRateLimiter(AbstractHeaderAuthenticator):
    """
    Each token in the cycle is checked against the rate limiter.
    If a token exceeds the capacity limit, the system switches to another token.
    If all tokens are exhausted, the system will enter a sleep state until
    the first token becomes available again.
    """

    DURATION = pendulum.duration(seconds=3600)  # Duration at which the current rate limit window resets

    def __init__(self, tokens: List[str], auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self._auth_method = auth_method
        self._auth_header = auth_header
        now = pendulum.now()
        self._tokens = {t: Token(count=5000, update_at=now, reset_at=now) for t in tokens}
        [self._check_token(t) for t in self._tokens]
        self._tokens_iter = cycle(self._tokens)
        self._active_token = next(self._tokens_iter)

    @property
    def auth_header(self) -> str:
        return self._auth_header

    @property
    def current_active_token(self) -> str:
        return self._active_token

    def update_token(self) -> None:
        self._active_token = next(self._tokens_iter)

    @property
    def token(self) -> str:
        while True:
            token = self.current_active_token
            if self._tokens[token].count > 0 and pendulum.now() - self._tokens[token].update_at <= self.DURATION:
                self._tokens[token].count -= 1
                return f"{self._auth_method} {token}"
            # self._check_token(token)
            self._active_token = next(self._tokens_iter)

            if all([x.count == 0 for x in self._tokens.values()]):
                min_time_to_wait_till_next_token_available = min((x.reset_at - pendulum.now()).in_seconds() for x in self._tokens.values())
                if min_time_to_wait_till_next_token_available > HttpStream.max_time:
                    time.sleep(min_time_to_wait_till_next_token_available)
                    [self._check_token(t) for t in self._tokens]
                else:
                    raise AirbyteTracedException(failure_type=FailureType.config_error, message="rate limits for all token were reached")

    def _check_token(self, token: str):
        """check that token is not limited"""
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        remaining_info = (
            requests.get(
                "https://api.github.com/rate_limit", headers=headers, auth=TokenAuthenticator(token, auth_method=self._auth_method)
            )
            .json()
            .get("resources")
            .get("core")
        )
        remaining_calls, reset_at = remaining_info.get("remaining"), pendulum.from_timestamp(remaining_info.get("reset"))
        token_info = self._tokens[token]
        token_info.reset_at = reset_at
        token_info.update_at = pendulum.now()
        token_info.count = remaining_calls
