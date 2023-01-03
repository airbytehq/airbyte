#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
from typing import Optional

import analytics
import click


def build_user_agent(octavia_version: str) -> str:
    """Build user-agent for the API client according to octavia version.

    Args:
        octavia_version (str): Current octavia version.

    Returns:
        str: the user-agent string.
    """
    return f"octavia-cli/{octavia_version}"


class TelemetryClient:

    WRITE_KEY = "ER8EjdRVFut7n05XPaaTKrSEnjLscyKr"

    def __init__(self, send_data: bool = False) -> None:
        """Create a TelemetryClient instance.

        Args:
            send_data (bool, optional): Whether the telemetry should be sent. Defaults to False.
        """
        self.segment_client = analytics.Client(self.write_key, send=send_data)

    @property
    def write_key(self) -> str:
        """Retrieve the write key according to environment.
        Developer can set the OCTAVIA_TELEMETRY_WRITE_KEY env var to send telemetry to another Segment source.

        Returns:
            str: The write key to use with the analytics client.
        """
        return os.getenv("OCTAVIA_TELEMETRY_WRITE_KEY", TelemetryClient.WRITE_KEY)

    def _create_command_name(self, ctx: click.Context, command_names: Optional[list] = None, extra_info_name: Optional[str] = None) -> str:
        """Build the full command name by concatenating info names the context and its parents.

        Args:
            ctx (click.Context): The click context from which we want to build the command name.
            command_names (Optional[list], optional): Previously builds commands name (used for recursion). Defaults to None.
            extra_info_name (Optional[str], optional): Extra info name if the context was not built yet. Defaults to None.

        Returns:
            str: The full command name.
        """
        if command_names is None:
            command_names = [ctx.info_name]
        else:
            command_names.insert(0, ctx.info_name)
        if ctx.parent is not None:
            self._create_command_name(ctx.parent, command_names)
        return " ".join(command_names) if not extra_info_name else " ".join(command_names + [extra_info_name])

    def send_command_telemetry(
        self, ctx: click.Context, error: Optional[Exception] = None, extra_info_name: Optional[str] = None, is_help: bool = False
    ):
        """Send telemetry with the analytics client.
        The event name is the command name.
        The context has the octavia version.
        The properties hold success or failure of command run, error type if exists and other metadata.

        Args:
            ctx (click.Context): Context from which the telemetry is built.
            error (Optional[Exception], optional): The error that was raised. Defaults to None.
            extra_info_name (Optional[str], optional): Extra info name if the context was not built yet. Defaults to None.
        """
        user_id = ctx.obj.get("WORKSPACE_ID") if ctx.obj.get("ANONYMOUS_DATA_COLLECTION", True) is False else None
        anonymous_id = None if user_id else "anonymous"
        segment_context = {"app": {"name": "octavia-cli", "version": ctx.obj.get("OCTAVIA_VERSION")}}
        segment_properties = {
            "success": error is None,
            "is_help": is_help,
            "error_type": error.__class__.__name__ if error is not None else None,
            "project_is_initialized": ctx.obj.get("PROJECT_IS_INITIALIZED"),
            "airbyter": os.getenv("AIRBYTE_ROLE") == "airbyter",
        }
        command_name = self._create_command_name(ctx, extra_info_name=extra_info_name)
        self.segment_client.track(
            user_id=user_id, anonymous_id=anonymous_id, event=command_name, properties=segment_properties, context=segment_context
        )
