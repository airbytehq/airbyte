#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from itertools import cycle
from types import SimpleNamespace as ns
from typing import List

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator


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


class MultipleTokenAuthenticatorWithRateLimiter(AbstractHeaderAuthenticator):
    """
    Each token in the cycle is checked against the rate limiter.
    If a token exceeds the capacity limit, the system switches to another token.
    If all tokens are exhausted, the system will enter a sleep state until
    the first token becomes available again.
    """

    DURATION = 3600  # seconds

    def __init__(self, tokens: List[str], requests_per_hour: int, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self._auth_method = auth_method
        self._auth_header = auth_header
        now = time.time()
        self._requests_per_hour = requests_per_hour
        self._tokens = {t: ns(count=self._requests_per_hour, update_at=now) for t in tokens}
        self._tokens_iter = cycle(self._tokens)

    @property
    def auth_header(self) -> str:
        return self._auth_header

    @property
    def token(self) -> str:
        while True:
            token = next(self._tokens_iter)
            if self._check_not_limited(token):
                return f"{self._auth_method} {token}"
            self._sleep()

    def _check_not_limited(self, token: str):
        """check that token is not limited"""
        now = time.time()
        if now - self._tokens[token].update_at >= self.DURATION:
            self._tokens[token].count = self._requests_per_hour
            self._tokens[token].update_at = now
        if self._tokens[token].count > 0:
            self._tokens[token].count -= 1
            return True

    def _sleep(self):
        if sum([ns.count for ns in self._tokens.values()]) == 0:
            sleep_time = self.DURATION - (time.time() - min([ns.update_at for ns in self._tokens.values()]))
            logging.warning("Sleeping for %.1f seconds to limit connector to %d requests per hour.", sleep_time, self._requests_per_hour)
            time.sleep(sleep_time)
