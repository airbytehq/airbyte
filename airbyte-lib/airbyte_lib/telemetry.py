# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import datetime
import os
from contextlib import suppress
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

import requests

from airbyte_lib.version import get_version


TRACKING_KEY = os.environ.get("AIRBYTE_TRACKING_KEY", "") or "cukeSffc0G6gFQehKDhhzSurDzVSZ2OP"


class SourceType(str, Enum):
    VENV = "venv"
    LOCAL_INSTALL = "local_install"


@dataclass
class CacheTelemetryInfo:
    type: str


streaming_cache_info = CacheTelemetryInfo("streaming")


class SyncState(str, Enum):
    STARTED = "started"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


@dataclass
class SourceTelemetryInfo:
    name: str
    type: SourceType
    version: str | None


def send_telemetry(
    source_info: SourceTelemetryInfo,
    cache_info: CacheTelemetryInfo,
    state: SyncState,
    number_of_records: int | None = None,
) -> None:
    # If DO_NOT_TRACK is set, we don't send any telemetry
    if os.environ.get("DO_NOT_TRACK"):
        return

    current_time: str = datetime.datetime.utcnow().isoformat()  # noqa: DTZ003 # prefer now() over utcnow()
    payload: dict[str, Any] = {
        "anonymousId": "airbyte-lib-user",
        "event": "sync",
        "properties": {
            "version": get_version(),
            "source": asdict(source_info),
            "state": state,
            "cache": asdict(cache_info),
            # explicitly set to 0.0.0.0 to avoid leaking IP addresses
            "ip": "0.0.0.0",
            "flags": {
                "CI": bool(os.environ.get("CI")),
            },
        },
        "timestamp": current_time,
    }
    if number_of_records is not None:
        payload["properties"]["number_of_records"] = number_of_records

    # Suppress exceptions if host is unreachable or network is unavailable
    with suppress(Exception):
        # Do not handle the response, we don't want to block the execution
        _ = requests.post("https://api.segment.io/v1/track", auth=(TRACKING_KEY, ""), json=payload)
