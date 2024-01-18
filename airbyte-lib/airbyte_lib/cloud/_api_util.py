"""These internal functions are used to interact with the Airbyte API (module named `airbyte`).

In order to insulate users from breaking changes and to avoid general confusion around naming
and design inconsistencies, we do not expose these functions or other Airbyte API classes within
AirbyteLib. Classes and functions from the Airbyte API external library should always be wrapped in
AirbyteLib classes - unless there's a very compelling reason to surface these models intentionally.
"""

from __future__ import annotations

import os
from time import sleep
from typing import Any

import airbyte as airbyte_api
from airbyte.models import operations as api_operations
from airbyte.models import shared as api_models
from airbyte.models.shared.jobcreaterequest import JobCreateRequest, JobTypeEnum

from airbyte_lib.exceptions import (
    HostedAirbyteError,
    HostedConnectionSyncError,
    MissingResourceError,
)


JOB_WAIT_INTERVAL_SECS = 2.0


def status_ok(status_code: int) -> bool:
    """Check if a status code is OK."""
    return status_code >= 200 and status_code < 300  # noqa: PLR2004  # allow inline magic numbers


def get_default_bearer_token() -> str:
    """Get the default bearer token from env variables."""
    return os.environ.get("AIRBYTE_API_KEY", None)


def get_airbyte_server_instance(
    *,
    api_key: str | None = None,
    api_root: str = "https://api.airbyte.com/v1",
) -> airbyte_api.Airbyte:
    """Get an Airbyte instance."""
    api_key = api_key or get_default_bearer_token()
    return airbyte_api.Airbyte(
        api_models.Security(
            bearer_auth=api_key,
        ),
        api_root=api_root,
    )


def get_workspace(
    workspace_id: str,
    *,
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
) -> api_models.WorkspaceResponse:
    """Get a connection."""
    api_key = api_key or get_default_bearer_token()
    airbyte_instance = get_airbyte_server_instance(
        api_key=api_key,
        api_root=api_root,
    )
    response = airbyte_instance.workspaces.get_workspace(
        api_operations.GetWorkspaceRequest(
            workspace_id=workspace_id,
        ),
    )
    if status_ok(response.status_code) and response.workspace_response:
        return response.workspace_response

    raise MissingResourceError(
        workspace_id,
        "workspace",
        more_info=response.text,
    )


def list_connections(
    workspace_id: str,
    *,
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
) -> list[api_models.ConnectionResponse]:
    """Get a connection."""
    _ = workspace_id  # Not used (yet)
    api_key = api_key or get_default_bearer_token()
    airbyte_instance = get_airbyte_server_instance(
        api_key=api_key,
        api_root=api_root,
    )
    response = airbyte_instance.connections.list_connections(
        api_operations.ListConnectionsRequest()(
            workspace_ids=[workspace_id],
        ),
    )

    if status_ok(response.status_code) and response.connections_response:
        return response.connections_response.data

    raise HostedAirbyteError(
        f"Failed to list connections from workspace {workspace_id}: {response.text}"
    )


def get_connection(
    workspace_id: str,
    connection_id: str,
    *,
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
) -> api_models.ConnectionResponse:
    """Get a connection."""
    _ = workspace_id  # Not used (yet)
    api_key = api_key or get_default_bearer_token()
    airbyte_instance = get_airbyte_server_instance(
        api_key=api_key,
        api_root=api_root,
    )
    response = airbyte_instance.connections.get_connection(
        api_models.GetConnectionRequest(
            connection_id=connection_id,
        ),
    )
    if status_ok(response.status_code) and response.connection_response:
        return response.connection_response

    raise MissingResourceError(connection_id, "connection", response.text)


def run_connection(
    workspace_id: str,
    connection_id: str,
    *,
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
    wait_for_job: bool = True,
    raise_on_failure: bool = True,
) -> api_models.ConnectionResponse:
    """Get a connection.

    If block is True, this will block until the connection is finished running.

    If raise_on_failure is True, this will raise an exception if the connection fails.
    """
    _ = workspace_id  # Not used (yet)
    api_key = api_key or get_default_bearer_token()
    airbyte_instance = get_airbyte_server_instance(
        api_key=api_key,
        api_root=api_root,
    )
    response = airbyte_instance.jobs.create_job(
        JobCreateRequest(
            connection_id=connection_id,
            job_type=JobTypeEnum.SYNC,
        ),
    )
    if status_ok(response.status_code) and response.job_response:
        if wait_for_job:
            job_info = wait_for_job(
                workspace_id=workspace_id,
                job_id=response.job_response.job_id,
                api_key=api_key,
                api_root=api_root,
                raise_on_failure=raise_on_failure,
            )

        return job_info

    raise HostedConnectionSyncError(f"Failed to run connection {connection_id}.", response.text)


def wait_for_job(
    workspace_id: str,
    job_id: str,
    *,
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
    raise_on_failure: bool = True,
) -> api_models.JobInfo:
    """Wait for a job to finish running."""
    _ = workspace_id  # Not used (yet)
    api_key = api_key or get_default_bearer_token()
    airbyte_instance = get_airbyte_server_instance(
        api_key=api_key,
        api_root=api_root,
    )
    while True:
        sleep(JOB_WAIT_INTERVAL_SECS)
        response = airbyte_instance.jobs.get_job(
            api_operations.GetJobRequest(
                job_id=job_id,
            ),
        )
        if status_ok(response.status_code) and response.job_info:
            job_info = response.job_info
            if job_info.status == api_models.StatusEnum.succeeded:
                return job_info

            if job_info.status == api_models.StatusEnum.failed:
                if raise_on_failure:
                    raise HostedConnectionSyncError(f"Job {job_id} failed: {job_info.message}")

                return job_info

            # Else: Job is still running
            pass
        else:
            raise MissingResourceError(job_id, "job", response.text)


def get_connection_by_name(
    workspace_id: str,
    connection_name: str,
    *,
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
) -> api_models.ConnectionResponse:
    """Get a connection."""
    connections = list_connections(
        workspace_id=workspace_id,
        api_key=api_key,
        api_root=api_root,
    )
    found: list[api_models.ConnectionResponse] = [
        connection for connection in connections if connection.name == connection_name
    ]
    if len(found) == 0:
        raise MissingResourceError(connection_name, "connection", f"Workspace: {workspace_id}")

    if len(found) > 1:
        raise Exception(
            f"Found multiple connections named '{connection_name}' in workspace '{workspace_id}': "
            f"'{found}'"
        )

    return found[0]


def get_source(
    source_id: str,
    *,
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
) -> api_models.SourceResponse:
    """Get a connection."""
    api_key = api_key or get_default_bearer_token()
    airbyte_instance = get_airbyte_server_instance(
        api_key=api_key,
        api_root=api_root,
    )
    response = airbyte_instance.sources.get_source(
        api_operations.GetSourceRequest(
            source_id=source_id,
        ),
    )
    if status_ok(response.status_code) and response.connection_response:
        return response.connection_response

    raise MissingResourceError(source_id, "source", response.text)


def create_source(
    name: str,
    *,
    workspace_id: str,
    config: dict[str, Any],
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
) -> api_models.SourceResponse:
    """Get a connection."""
    api_key = api_key or get_default_bearer_token()
    airbyte_instance = get_airbyte_server_instance(
        api_key=api_key,
        api_root=api_root,
    )
    response = airbyte_instance.sources.create_source(
        api_models.SourceCreateRequest(
            name=name,
            workspace_id=workspace_id,
            configuration=config,  # TODO: wrap in a proper configuration object
            definition_id=None,  # Not used alternative to config.sourceType.
            secret_id=None,  # For OAuth, not yet supported
        ),
    )
    if status_ok(response.status_code) and response.connection_response:
        return response.source_response

    raise HostedAirbyteError("Could not create source.")


def get_destination(
    destination_id: str,
    *,
    api_root: str = "https://api.airbyte.com/v1",
    api_key: str | None = None,
) -> api_models.DestinationResponse:
    """Get a connection."""
    api_key = api_key or get_default_bearer_token()
    airbyte_instance = get_airbyte_server_instance(
        api_key=api_key,
        api_root=api_root,
    )
    response = airbyte_instance.sources.get_destination(
        api_operations.GetDestinationRequest(
            destination_id=destination_id,
        ),
    )
    if status_ok(response.status_code) and response.connection_response:
        return response.connection_response

    raise MissingResourceError(destination_id, "destination", response.text)
