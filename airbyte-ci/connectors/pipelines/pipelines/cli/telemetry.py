#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import getpass
import hashlib
import os
import platform
import sys

import segment.analytics as analytics
from asyncclick import get_current_context

analytics.write_key = "G6G7whgro81g9xM00kN2buclGKvcOjFd"
analytics.send = True
analytics.debug = False


def _is_airbyte_user():
    """Returns True if the user is airbyter, False otherwise."""
    return os.getenv("AIRBYTE_ROLE") == "airbyter"


def _get_anonymous_system_id():
    """Returns a unique anonymous hashid of the current system info."""
    # Collect machine-specific information
    machine_info = platform.node()
    username = getpass.getuser()

    unique_system_info = f"{machine_info}-{username}"

    # Generate a unique hash
    unique_id = hashlib.sha256(unique_system_info.encode()).hexdigest()

    return unique_id


def click_track_command(f):
    """
    Decorator to track CLI commands with segment.io
    """

    def wrapper(*args, **kwargs):
        ctx = get_current_context()
        top_level_command = ctx.command_path
        full_cmd = " ".join(sys.argv)

        # remove anything prior to the command name f.__name__
        # to avoid logging inline secrets
        santized_cmd = full_cmd[full_cmd.find(top_level_command) :]

        sys_id = _get_anonymous_system_id()
        sys_user_name = f"anonymous:{sys_id}"
        airbyter = _is_airbyte_user()

        is_local = kwargs.get("is_local", False)
        user_id = "local-user" if is_local else "ci-user"
        event = f"airbyte-ci:{f.__name__}"

        # IMPORTANT! do not log kwargs as they may contain secrets
        analytics.track(user_id, event, {"username": sys_user_name, "command": santized_cmd, "airbyter": airbyter})

        return f(*args, **kwargs)

    return wrapper
