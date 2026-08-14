#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import contextlib
from typing import Any

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


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


def rotate_authenticator_token(authenticator: Any) -> bool:
    """Force the shared `RateLimitedMultipleTokenAuthenticator` onto its next token.

    GitHub can rate-limit a request whose *local* counters still look healthy: the token is
    shared with another connection, requests were in flight when the counters were seeded, or
    a secondary rate limit (tracked separately from the primary quota) was hit. The CDK
    authenticator only rotates proactively, when its own counter for a quota pool reaches
    zero, so the error path has to push it.

    Returns False when there is nothing to rotate (a single configured token, or an
    authenticator that doesn't expose rotation) so callers can fall back to waiting.

    TODO: replace the private-attribute path with the public CDK rotation hook once
    `RateLimitedMultipleTokenAuthenticator` exposes one. The manifest error handler needs the
    same hook — see the note on `WaitUntilTimeFromHeader` in `manifest.yaml`.
    """
    rotate = getattr(authenticator, "rotate_token", None)  # future CDK public API
    if callable(rotate):
        rotate()
        return True

    tokens_iter = getattr(authenticator, "_tokens_iter", None)
    if tokens_iter is None or len(getattr(authenticator, "_tokens", ())) < 2:
        return False
    with getattr(authenticator, "_lock", contextlib.nullcontext()):
        authenticator._active_token = next(tokens_iter)
    return True
