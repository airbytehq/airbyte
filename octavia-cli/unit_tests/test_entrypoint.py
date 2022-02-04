#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import click
import pytest
from click.testing import CliRunner
from octavia_cli import entrypoint


@click.command()
@click.pass_context
def dumb(ctx):
    pass


def test_octavia(mocker):
    mocker.patch.object(entrypoint, "click")
    mocker.patch.object(entrypoint, "get_api_client")
    mocker.patch.object(entrypoint, "get_workspace_id", mocker.Mock(return_value="api-defined-workspace-id"))
    mocker.patch.object(entrypoint, "check_is_initialized", mocker.Mock(return_value=True))
    context_object = {}
    entrypoint.octavia.add_command(dumb)
    runner = CliRunner()
    result = runner.invoke(entrypoint.octavia, ["--airbyte-url", "test-airbyte-url", "dumb"], obj=context_object)
    entrypoint.get_api_client.assert_called()
    entrypoint.get_workspace_id.assert_called_with(entrypoint.get_api_client.return_value, None)
    expected_message = "🐙 - Octavia is targetting your Airbyte instance running at test-airbyte-url on workspace api-defined-workspace-id."
    entrypoint.click.style.assert_called_with(expected_message, fg="green")
    entrypoint.click.echo.assert_called_with(entrypoint.click.style.return_value)
    assert context_object == {
        "API_CLIENT": entrypoint.get_api_client.return_value,
        "WORKSPACE_ID": entrypoint.get_workspace_id.return_value,
        "PROJECT_IS_INITIALIZED": entrypoint.check_is_initialized.return_value,
    }
    assert result.exit_code == 0


def test_octavia_not_initialized(mocker):
    mocker.patch.object(entrypoint, "click")
    mocker.patch.object(entrypoint, "get_api_client")
    mocker.patch.object(entrypoint, "get_workspace_id", mocker.Mock(return_value="api-defined-workspace-id"))
    mocker.patch.object(entrypoint, "check_is_initialized", mocker.Mock(return_value=False))
    context_object = {}
    entrypoint.octavia.add_command(dumb)
    runner = CliRunner()
    result = runner.invoke(entrypoint.octavia, ["--airbyte-url", "test-airbyte-url", "dumb"], obj=context_object)
    entrypoint.click.style.assert_called_with("🐙 - Project is not yet initialized.", fg="red", bold=True)
    entrypoint.click.echo.assert_called_with(entrypoint.click.style.return_value)
    assert result.exit_code == 0


def test_get_api_client(mocker):
    mocker.patch.object(entrypoint, "airbyte_api_client")
    mocker.patch.object(entrypoint, "check_api_health")
    api_client = entrypoint.get_api_client("test-url")
    entrypoint.airbyte_api_client.Configuration.assert_called_with(host="test-url/api")
    entrypoint.airbyte_api_client.ApiClient.assert_called_with(entrypoint.airbyte_api_client.Configuration.return_value)
    entrypoint.check_api_health.assert_called_with(entrypoint.airbyte_api_client.ApiClient.return_value)
    assert api_client == entrypoint.airbyte_api_client.ApiClient.return_value


def test_get_workspace_id_user_defined(mocker):
    mock_api_client = mocker.Mock()
    mocker.patch.object(entrypoint, "check_workspace_exists")
    mocker.patch.object(entrypoint, "workspace_api")
    assert entrypoint.get_workspace_id(mock_api_client, "user-defined-workspace-id") == "user-defined-workspace-id"
    entrypoint.check_workspace_exists.assert_called_with(mock_api_client, "user-defined-workspace-id")


def test_get_workspace_id_api_defined(mocker):
    mock_api_client = mocker.Mock()
    mocker.patch.object(entrypoint, "check_workspace_exists")
    mocker.patch.object(entrypoint, "workspace_api")
    mock_api_instance = entrypoint.workspace_api.WorkspaceApi.return_value
    mock_api_instance.list_workspaces.return_value = mocker.Mock(workspaces=[{"workspaceId": "api-defined-workspace-id"}])
    assert entrypoint.get_workspace_id(mock_api_client, None) == "api-defined-workspace-id"
    entrypoint.workspace_api.WorkspaceApi.assert_called_with(mock_api_client)
    mock_api_instance.list_workspaces.assert_called_with(_check_return_type=False)


def test_commands_in_octavia_group():
    octavia_commands = entrypoint.octavia.commands.values()
    for command in entrypoint.AVAILABLE_COMMANDS:
        assert command in octavia_commands


@pytest.mark.parametrize(
    "command",
    [entrypoint.apply, entrypoint.create, entrypoint.delete, entrypoint._import],
)
def test_not_implemented_commands(command):
    runner = CliRunner()
    result = runner.invoke(command)
    assert result.exit_code == 1
    assert result.output.endswith("not yet implemented.\n")


def test_available_commands():
    assert entrypoint.AVAILABLE_COMMANDS == [entrypoint.list_commands._list, entrypoint.init_commands.init]
