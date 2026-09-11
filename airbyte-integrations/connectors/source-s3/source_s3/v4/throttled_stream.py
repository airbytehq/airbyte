#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""
ThrottledFileBasedStream wraps DefaultFileBasedStream's `read()` to limit how
often it emits STATE messages.

source-s3 uses the legacy DefaultFileBasedCursor path, where the framework
emits a state message after every slice (one file). On streams with thousands
of files the cursor's history dict carried in each state message grows with
the sync, and the platform/orchestrator buffer of un-ACKed state messages
OOMs the replication pod before the destination ACKs them (oncall #12663).

The wrapper observes the message stream produced by the parent `read()` and:
  * passes through every non-STATE message unchanged,
  * forwards the first STATE message immediately (cold start),
  * suppresses any subsequent STATE message inside the throttle window and
    keeps a reference to the most recent suppressed one,
  * yields the held STATE at the very end of the iterator so the destination
    always sees the latest cursor at end of stream.

Localized to source-s3 — no CDK change required.
"""

from __future__ import annotations

import time
from typing import Any, Iterable, Optional

from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.file_based.stream.default_file_based_stream import (
    DefaultFileBasedStream,
)
from airbyte_cdk.sources.streams.core import StreamData


class ThrottledFileBasedStream(DefaultFileBasedStream):
    """File-based stream that throttles STATE-message emissions to at most one
    per `state_emission_throttle_seconds` seconds.

    The latest suppressed STATE is kept so the stream can emit a final
    checkpoint when the parent iterator finishes inside the throttle window.
    """

    # Subclasses can override. Default = 600 s (10 min) — same cadence as the
    # CDK's ConcurrentPerPartitionCursor throttle.
    state_emission_throttle_seconds: float = 600.0

    def read(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Iterable[StreamData]:
        throttle = self.state_emission_throttle_seconds
        last_emit_at: float = 0.0
        pending_state: Optional[AirbyteMessage] = None

        for message in super().read(*args, **kwargs):
            if isinstance(message, AirbyteMessage) and message.type == MessageType.STATE:
                now = time.time()
                if now - last_emit_at < throttle:
                    # Keep only the latest suppressed checkpoint. If the stream
                    # finishes before another STATE crosses the throttle window,
                    # this becomes the final checkpoint emitted below.
                    pending_state = message
                    continue
                last_emit_at = now
                pending_state = None
            yield message

        # Emit the latest suppressed checkpoint when the sync ends inside the
        # throttle window, so completed syncs do not finish with stale state.
        if pending_state is not None:
            yield pending_state
