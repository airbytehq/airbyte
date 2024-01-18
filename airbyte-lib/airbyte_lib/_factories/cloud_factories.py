# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from airbyte_lib.cloud.connections import HostedConnection


def get_cloud_connection(
    workspace_id: str,
    connection_id: str,
    *,
    api_key: str | None = None,
) -> HostedConnection:
    """Get a connection object.

    TODO: Decide on naming for this function.
    Should it be `get_hosted_connection` or `get_connection` or `get_cloud_connection`?
    """
    return HostedConnection(
        workspace_id=workspace_id,
        connection_id=connection_id,
        api_key=api_key,
    )
