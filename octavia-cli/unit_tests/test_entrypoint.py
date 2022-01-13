#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest import mock

import click
import pytest
from click.testing import CliRunner
from octavia_cli import entrypoint


@click.command()
@click.pass_context
def dumb(ctx):
    pass


def test_octavia(mocker):
    mocker.patch.object(entrypoint, "workspace_api")
    mocker.patch.object(entrypoint, "airbyte_api_client")

    context_object = {}
    mock_api_instance = entrypoint.workspace_api.WorkspaceApi.return_value
    mock_api_instance.list_workspaces.return_value = mock.MagicMock(workspaces=[{"workspaceId": "expected_workspace_id"}])

    entrypoint.octavia.add_command(dumb)
    runner = CliRunner()
    result = runner.invoke(entrypoint.octavia, ["--airbyte-url", "test-airbyte-url", "dumb"], obj=context_object)
    entrypoint.airbyte_api_client.Configuration.assert_called_with(host="test-airbyte-url/api")
    entrypoint.airbyte_api_client.ApiClient.assert_called_with(entrypoint.airbyte_api_client.Configuration.return_value)
    entrypoint.workspace_api.WorkspaceApi.assert_called_with(entrypoint.airbyte_api_client.ApiClient.return_value)
    mock_api_instance.list_workspaces.assert_called_once()
    assert context_object["API_CLIENT"] == entrypoint.airbyte_api_client.ApiClient.return_value
    assert context_object["WORKSPACE_ID"] == "expected_workspace_id"
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "command",
    [entrypoint.init, entrypoint.apply, entrypoint.create, entrypoint.delete, entrypoint._list, entrypoint._import],
)
def test_not_implemented_commands(command):
    runner = CliRunner()
    result = runner.invoke(command)
    assert result.exit_code == 1
    assert result.output.endswith("not yet implemented.\n")
