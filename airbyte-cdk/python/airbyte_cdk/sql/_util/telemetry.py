# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Telemetry implementation for Airbyte.

We track some basic telemetry to help us understand how Airbyte is used. You can opt-out of
telemetry at any time by setting the environment variable DO_NOT_TRACK to any value.

If you are able to provide telemetry, it is greatly appreciated. Telemetry helps us understand how
the library is used, what features are working. We also use this telemetry to prioritize bug fixes
and improvements to the connectors themselves, focusing first on connectors that are (1) most used
and (2) report the most sync failures as a percentage of total attempted syncs.

Your privacy and security are our priority. We do not track any PII (personally identifiable
information), nor do we track anything that _could_ contain PII without first hashing the data
using a one-way hash algorithm. We only track the minimum information necessary to understand how
Airbyte is used, and to dedupe users to determine how many users or use cases there are.


Here is what is tracked:
- The version of Airbyte.
- The Python version.
- The OS.
- The source type (venv or local install).
- The source name and version number.
- The state of the sync (started, failed, succeeded).
- The cache type (Snowflake, Postgres, etc.).
- The number of records processed.
- The application hash, which is a hash of either the notebook name or Python script name.
- Flags to help us understand if Airbyte is running on CI, Google Colab, or another environment.

"""

from __future__ import annotations

import datetime
import os
from contextlib import suppress
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import requests
import ulid
import yaml
from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._util import meta
from airbyte_cdk.sql._util.connector_info import ConnectorRuntimeInfo, WriterRuntimeInfo
from airbyte_cdk.sql._util.hashing import one_way_hash
from airbyte_cdk.sql.version import get_version

DEBUG = True
"""Enable debug mode for telemetry code."""


Airbyte_APP_TRACKING_KEY = os.environ.get("AIRBYTE_TRACKING_KEY", "") or "cukeSffc0G6gFQehKDhhzSurDzVSZ2OP"
"""This key corresponds globally to the "Airbyte" application."""


Airbyte_SESSION_ID = str(ulid.ULID())
"""Unique identifier for the current invocation of Airbyte.

This is used to determine the order of operations within a specific session.
It is not a unique identifier for the user.
"""


DO_NOT_TRACK = "DO_NOT_TRACK"
"""Environment variable to opt-out of telemetry."""

_ENV_ANALYTICS_ID = "AIRBYTE_ANALYTICS_ID"  # Allows user to override the anonymous user ID
_ANALYTICS_FILE = Path.home() / ".airbyte" / "analytics.yml"
_ANALYTICS_ID: str | bool | None = None

UNKNOWN = "unknown"


def _setup_analytics() -> str | bool:
    """Set up the analytics file if it doesn't exist.

    Return the anonymous user ID or False if the user has opted out.
    """
    anonymous_user_id: str | None = None
    issues: list[str] = []

    if os.environ.get(DO_NOT_TRACK):
        # User has opted out of tracking.
        return False

    if _ENV_ANALYTICS_ID in os.environ:
        # If the user has chosen to override their analytics ID, use that value and
        # remember it for future invocations.
        anonymous_user_id = os.environ[_ENV_ANALYTICS_ID]

    if not _ANALYTICS_FILE.exists():
        # This is a one-time message to inform the user that we are tracking anonymous usage stats.
        print(
            "Thank you for using Airbyte!\n"
            "Anonymous usage reporting is currently enabled. For more information, please"
            " see https://docs.airbyte.com/telemetry"
        )

    if _ANALYTICS_FILE.exists():
        analytics_text = _ANALYTICS_FILE.read_text()
        try:
            analytics: dict[str, str | bool] = yaml.safe_load(analytics_text)
        except Exception as ex:
            issues += f"File appears corrupted. Error was: {ex!s}"

        if analytics and "anonymous_user_id" in analytics:
            # The analytics ID was successfully located.
            if not anonymous_user_id:
                return analytics["anonymous_user_id"]

            if anonymous_user_id == analytics["anonymous_user_id"]:
                # Values match, no need to update the file.
                return analytics["anonymous_user_id"]

            issues.append("Provided analytics ID did not match the file. Rewriting the file.")
            print(f"Received a user-provided analytics ID override in the '{_ENV_ANALYTICS_ID}' " "environment variable.")

    # File is missing, incomplete, or stale. Create a new one.
    anonymous_user_id = anonymous_user_id or str(ulid.ULID())
    try:
        _ANALYTICS_FILE.parent.mkdir(exist_ok=True, parents=True)
        _ANALYTICS_FILE.write_text(
            "# This file is used by Airbyte to track anonymous usage statistics.\n"
            "# For more information or to opt out, please see\n"
            "# - https://docs.airbyte.com/operator-guides/telemetry\n"
            f"anonymous_user_id: {anonymous_user_id}\n"
        )
    except Exception:
        # Failed to create the analytics file. Likely due to a read-only filesystem.
        issues.append("Failed to write the analytics file. Check filesystem permissions.")
        pass

    if DEBUG and issues:
        nl = "\n"
        print(f"One or more issues occurred when configuring usage tracking:\n{nl.join(issues)}")

    return anonymous_user_id


def _get_analytics_id() -> str | None:
    result: str | bool | None = _ANALYTICS_ID
    if result is None:
        result = _setup_analytics()

    if result is False:
        return None

    return cast(str, result)


_ANALYTICS_ID = _get_analytics_id()


class EventState(str, Enum):
    STARTED = "started"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class EventType(str, Enum):
    INSTALL = "install"
    SYNC = "sync"
    VALIDATE = "validate"
    CHECK = "check"


@lru_cache
def get_env_flags() -> dict[str, Any]:
    flags: dict[str, bool | str] = {
        "CI": meta.is_ci(),
        "LANGCHAIN": meta.is_langchain(),
        "NOTEBOOK_RUNTIME": (
            "GOOGLE_COLAB" if meta.is_colab() else "JUPYTER" if meta.is_jupyter() else "VS_CODE" if meta.is_vscode_notebook() else False
        ),
    }
    # Drop these flags if value is False or None
    return {k: v for k, v in flags.items() if v is not None and v is not False}


def send_telemetry(
    *,
    source: ConnectorRuntimeInfo | None,
    destination: ConnectorRuntimeInfo | None,
    cache: WriterRuntimeInfo | None,
    state: EventState,
    event_type: EventType,
    number_of_records: int | None = None,
    exception: Exception | None = None,
) -> None:
    # If DO_NOT_TRACK is set, we don't send any telemetry
    if os.environ.get(DO_NOT_TRACK):
        return

    payload_props: dict[str, str | int | dict[str, Any]] = {
        "session_id": Airbyte_SESSION_ID,
        "state": state,
        "version": get_version(),
        "python_version": meta.get_python_version(),
        "os": meta.get_os(),
        "application_hash": one_way_hash(meta.get_application_name()),
        "flags": get_env_flags(),
    }

    if source:
        payload_props["source"] = source.to_dict()

    if destination:
        payload_props["destination"] = destination.to_dict()

    if cache:
        payload_props["cache"] = cache.to_dict()

    if exception:
        if isinstance(exception, exc.AirbyteError):
            payload_props["exception"] = exception.safe_logging_dict()
        else:
            payload_props["exception"] = {"class": type(exception).__name__}

    if number_of_records is not None:
        payload_props["number_of_records"] = number_of_records

    # Suppress exceptions if host is unreachable or network is unavailable
    with suppress(Exception):
        # Do not handle the response, we don't want to block the execution
        _ = requests.post(
            "https://api.segment.io/v1/track",
            auth=(Airbyte_APP_TRACKING_KEY, ""),
            json={
                "anonymousId": _get_analytics_id(),
                "event": event_type,
                "properties": payload_props,
                "timestamp": datetime.datetime.utcnow().isoformat(),  # noqa: DTZ003
            },
        )


def log_config_validation_result(
    name: str,
    state: EventState,
    exception: Exception | None = None,
) -> None:
    """Log a config validation event.

    If the name starts with "destination-", it is treated as a destination name. Otherwise, it is
    treated as a source name.
    """
    send_telemetry(
        source=ConnectorRuntimeInfo(name=name) if not name.startswith("destination-") else None,
        destination=ConnectorRuntimeInfo(name=name) if name.startswith("destination-") else None,
        cache=None,
        state=state,
        event_type=EventType.VALIDATE,
        exception=exception,
    )


def log_connector_check_result(
    name: str,
    state: EventState,
    exception: Exception | None = None,
) -> None:
    """Log a connector `check` result.

    If the name starts with "destination-", it is treated as a destination name. Otherwise, it is
    treated as a source name.
    """
    send_telemetry(
        source=ConnectorRuntimeInfo(name=name) if not name.startswith("destination-") else None,
        destination=ConnectorRuntimeInfo(name=name) if name.startswith("destination-") else None,
        cache=None,
        state=state,
        event_type=EventType.CHECK,
        exception=exception,
    )


def log_install_state(
    name: str,
    state: EventState,
    exception: Exception | None = None,
) -> None:
    """Log an install event."""
    send_telemetry(
        source=ConnectorRuntimeInfo(name=name),
        destination=None,
        cache=None,
        state=state,
        event_type=EventType.INSTALL,
        exception=exception,
    )
