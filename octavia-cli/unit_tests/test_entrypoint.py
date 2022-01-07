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


@mock.patch("octavia_cli.entrypoint.workspace_api")
@mock.patch("octavia_cli.entrypoint.airbyte_api_client")
def test_octavia(mock_airbyte_api_client: mock.Mock, mock_workspace_api: mock.Mock):
    context_object = {}
    mock_api_instance = mock_workspace_api.WorkspaceApi.return_value
    mock_api_instance.list_workspaces.return_value = mock.MagicMock(workspaces=[mock.MagicMock(workspace_id="expected_workspace_id")])

    entrypoint.octavia.add_command(dumb)
    runner = CliRunner()
    result = runner.invoke(entrypoint.octavia, ["--airbyte-url", "test-airbyte-url", "dumb"], obj=context_object)
    mock_airbyte_api_client.Configuration.assert_called_with(host="test-airbyte-url/api")
    mock_airbyte_api_client.ApiClient.assert_called_with(mock_airbyte_api_client.Configuration.return_value)
    mock_workspace_api.WorkspaceApi.assert_called_with(mock_airbyte_api_client.ApiClient.return_value)
    mock_api_instance.list_workspaces.assert_called_once()
    assert context_object["API_CLIENT"] == mock_airbyte_api_client.ApiClient.return_value
    assert context_object["WORKSPACE_ID"] == "expected_workspace_id"
    assert result.exit_code == 0


def test_commands_in_octavia_group():
    octavia_commands = entrypoint.octavia.commands.values()
    for command in entrypoint.AVAILABLE_COMMANDS:
        assert command in octavia_commands


@pytest.mark.parametrize(
    "command",
    [entrypoint.init, entrypoint.apply, entrypoint.create, entrypoint.delete, entrypoint._import],
)
def test_not_implemented_commands(command):
    runner = CliRunner()
    result = runner.invoke(command)
    assert result.exit_code == 1
    assert result.output.endswith("not yet implemented.\n")
