#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from itertools import cycle
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
    """Github rate limiter"""

    duration = 3600  # seconds

    def __init__(self, tokens: List[str], requests: int, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self._auth_method = auth_method
        self._auth_header = auth_header
        self._tokens = tokens
        self._tokens_iter = cycle(self._tokens)

        self.capacity = requests
        self.stat = {}
        for t in tokens:
            self.stat[t] = {"items": requests, "timestamp": None}

    @property
    def auth_header(self) -> str:
        return self._auth_header

    @property
    def token(self) -> str:
        now = time.time()
        while True:
            t = next(self._tokens_iter)
            res = self._check_rate_limit(t, now)
            if res:
                return f"{self._auth_method} {t}"

            # do we need to sleep ?
            if sum([v["items"] for k, v in self.stat.items()]) == 0:
                min_t = min([v["timestamp"] for k, v in self.stat.items()])
                sleep_time = self.duration - (now - min_t)
                logging.warning("sleeping %d", sleep_time)
                time.sleep(self.duration - (now - min_t))

    def _check_rate_limit(self, t, now):

        if self.stat[t]["timestamp"] is None:
            self.stat[t]["timestamp"] = now

        if now - self.stat[t]["timestamp"] >= self.duration:
            self.stat[t]["timestamp"] = now
            self.stat[t]["items"] = self.capacity

        if self.stat[t]["items"] > 0:
            self.stat[t]["items"] -= 1
            return True

        return False
