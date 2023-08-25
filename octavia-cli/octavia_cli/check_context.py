#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import click
from urllib3.exceptions import MaxRetryError

import airbyte_api_client
from airbyte_api_client.api import health_api, workspace_api
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody

from .init.commands import DIRECTORIES_TO_CREATE as REQUIRED_PROJECT_DIRECTORIES


class UnhealthyApiError(click.ClickException):
    pass


class UnreachableAirbyteInstanceError(click.ClickException):
    pass


class WorkspaceIdError(click.ClickException):
    pass


class ProjectNotInitializedError(click.ClickException):
    pass


def check_api_health(api_client: airbyte_api_client.ApiClient) -> None:
    """Check if the Airbyte API is network reachable and healthy.

    Args:
        api_client (airbyte_api_client.ApiClient): Airbyte API client.

    Raises:
        click.ClickException: Raised if the Airbyte api server is unavailable according to the API response.
        click.ClickException: Raised if the Airbyte URL is not reachable.
    """
    api_instance = health_api.HealthApi(api_client)
    try:
        api_response = api_instance.get_health_check()
        if not api_response.available:
            msg = "Your Airbyte instance is not ready to receive requests: the health endpoint returned 'available: False.'"
            raise UnhealthyApiError(
                msg,
            )
    except (airbyte_api_client.ApiException, MaxRetryError) as e:
        msg = f"Could not reach your Airbyte instance, make sure the instance is up and running and network reachable: {e}"
        raise UnreachableAirbyteInstanceError(
            msg,
        )


def check_workspace_exists(api_client: airbyte_api_client.ApiClient, workspace_id: str) -> None:
    """Check if the provided workspace id corresponds to an existing workspace on the Airbyte instance.

    Args:
        api_client (airbyte_api_client.ApiClient): Airbyte API client.
        workspace_id (str): Id of the workspace whose existence we are trying to verify.

    Raises:
        click.ClickException: Raised if the workspace does not exist on the Airbyte instance.
    """
    api_instance = workspace_api.WorkspaceApi(api_client)
    try:
        api_instance.get_workspace(WorkspaceIdRequestBody(workspace_id=workspace_id), _check_return_type=False)
    except airbyte_api_client.ApiException:
        msg = "The workspace you are trying to use does not exist in your Airbyte instance"
        raise WorkspaceIdError(msg)


def check_is_initialized(project_directory: str = ".") -> bool:
    """Check if required project directories exist to consider the project as initialized.

    Args:
        project_directory (str, optional): Where the project should be initialized. Defaults to ".".

    Returns:
        bool: [description]
    """
    sub_directories = [f.name for f in os.scandir(project_directory) if f.is_dir()]
    return set(REQUIRED_PROJECT_DIRECTORIES).issubset(sub_directories)


def requires_init(f):
    def wrapper(ctx, **kwargs):
        if not ctx.obj["PROJECT_IS_INITIALIZED"]:
            msg = "Your octavia project is not initialized, please run 'octavia init' before running this command."
            raise ProjectNotInitializedError(
                msg,
            )
        f(ctx, **kwargs)

    return wrapper
