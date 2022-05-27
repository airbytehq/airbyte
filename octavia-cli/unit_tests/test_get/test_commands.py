#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from click.testing import CliRunner
from octavia_cli.get import commands


def test_commands_in_get_group():
    get_commands = commands.get.commands.values()
    for command in commands.AVAILABLE_COMMANDS:
        assert command in get_commands


@pytest.fixture
def context_object(mock_api_client, mock_telemetry_client):
    return {
        "API_CLIENT": mock_api_client,
        "WORKSPACE_ID": "my_workspace_id",
        "resource_id": "my_resource_id",
        "TELEMETRY_CLIENT": mock_telemetry_client,
    }


def test_available_commands():
    assert commands.AVAILABLE_COMMANDS == [commands.source, commands.destination, commands.connection]


@pytest.mark.parametrize(
    "command,resource_id",
    [
        (commands.source, "my_resource_id"),
    ],
)
def test_source(mocker, context_object, command, resource_id):
    runner = CliRunner()
    mocker.patch.object(commands, "Source", mocker.Mock())
    mock_renderer = commands.Source.return_value
    mock_renderer.get_config.return_value = '{"hello": "world"}'
    result = runner.invoke(command, [resource_id], obj=context_object)
    assert result.exit_code == 0
    commands.Source.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], resource_id)


@pytest.mark.parametrize(
    "command,resource_id",
    [
        (commands.destination, "my_resource_id"),
    ],
)
def test_destination(mocker, context_object, command, resource_id):
    runner = CliRunner()
    mocker.patch.object(commands, "Destination", mocker.Mock())
    mock_renderer = commands.Destination.return_value
    mock_renderer.get_config.return_value = '{"hello": "world"}'
    result = runner.invoke(command, [resource_id], obj=context_object)
    assert result.exit_code == 0
    commands.Destination.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], resource_id)


@pytest.mark.parametrize(
    "command,resource_id",
    [
        (commands.connection, "my_resource_id"),
    ],
)
def test_connection(mocker, context_object, command, resource_id):
    runner = CliRunner()
    mocker.patch.object(commands, "Connection", mocker.Mock())
    mock_renderer = commands.Connection.return_value
    mock_renderer.get_config.return_value = '{"hello": "world"}'
    result = runner.invoke(command, [resource_id], obj=context_object)
    assert result.exit_code == 0
    commands.Connection.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], resource_id)
