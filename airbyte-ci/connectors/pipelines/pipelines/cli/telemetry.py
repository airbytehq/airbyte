#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import getpass
import hashlib
import os
import platform
import sys
from typing import TYPE_CHECKING

import segment.analytics as analytics  # type: ignore
from asyncclick import get_current_context

DISABLE_TELEMETRY = os.environ.get("AIRBYTE_CI_DISABLE_TELEMETRY", "false").lower() == "true"

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Tuple

    from asyncclick import Command

analytics.write_key = "G6G7whgro81g9xM00kN2buclGKvcOjFd"
analytics.send = not DISABLE_TELEMETRY
analytics.debug = False


def _is_airbyte_user() -> bool:
    """Returns True if the user is airbyter, False otherwise."""
    return os.getenv("AIRBYTE_ROLE") == "airbyter"


def _get_anonymous_system_id() -> str:
    """Returns a unique anonymous hashid of the current system info."""
    # Collect machine-specific information
    machine_info = platform.node()
    username = getpass.getuser()

    unique_system_info = f"{machine_info}-{username}"

    # Generate a unique hash
    unique_id = hashlib.sha256(unique_system_info.encode()).hexdigest()

    return unique_id


def click_track_command(f: Callable) -> Callable:
    """
    Decorator to track CLI commands with segment.io
    """

    def wrapper(*args: Tuple, **kwargs: Dict[str, Any]) -> Command:
        ctx = get_current_context()

        top_level_command = ctx.command_path
        full_cmd = " ".join(sys.argv)

        # remove anything prior to the command name f.__name__
        # to avoid logging inline secrets
        sanitized_cmd = full_cmd[full_cmd.find(top_level_command) :]
        sys_id = _get_anonymous_system_id()
        sys_user_name = f"anonymous:{sys_id}"
        airbyter = _is_airbyte_user()

        is_local = kwargs.get("is_local", False)
        user_id = "local-user" if is_local else "ci-user"
        event = f"airbyte-ci:{f.__name__}"

        # IMPORTANT! do not log kwargs as they may contain secrets
        analytics.track(user_id, event, {"username": sys_user_name, "command": sanitized_cmd, "airbyter": airbyter})

        return f(*args, **kwargs)

    return wrapper
