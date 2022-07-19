#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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


def test_build_help_message():
    assert commands.build_help_message("fake_resource_type") == "Get a JSON representation of a remote fake_resource_type."


def test_get_resource_id_or_name():
    resource_id, resource_name = commands.get_resource_id_or_name("resource_name")
    assert resource_id is None and resource_name == "resource_name"
    resource_id, resource_name = commands.get_resource_id_or_name("8c2e8369-3b81-471a-9945-32a3c67c31b7")
    assert resource_id == "8c2e8369-3b81-471a-9945-32a3c67c31b7" and resource_name is None


def test_get_json_representation(mocker, context_object):
    mock_cls = mocker.Mock()
    mocker.patch.object(commands.click, "echo")
    mock_resource_id = mocker.Mock()
    mock_resource_name = mocker.Mock()
    mocker.patch.object(commands, "get_resource_id_or_name", mocker.Mock(return_value=(mock_resource_id, mock_resource_name)))
    json_repr = commands.get_json_representation(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], mock_cls, "resource_to_get")
    commands.get_resource_id_or_name.assert_called_with("resource_to_get")
    mock_cls.assert_called_with(
        context_object["API_CLIENT"], context_object["WORKSPACE_ID"], resource_id=mock_resource_id, resource_name=mock_resource_name
    )
    assert json_repr == mock_cls.return_value.to_json.return_value


@pytest.mark.parametrize(
    "command, resource_cls, resource",
    [
        (commands.source, commands.Source, "my_resource_id"),
        (commands.destination, commands.Destination, "my_resource_id"),
        (commands.connection, commands.Connection, "my_resource_id"),
    ],
)
def test_commands(context_object, mocker, command, resource_cls, resource):
    mocker.patch.object(commands, "get_json_representation", mocker.Mock(return_value='{"foo": "bar"}'))
    runner = CliRunner()
    result = runner.invoke(command, [resource], obj=context_object)
    commands.get_json_representation.assert_called_once_with(
        context_object["API_CLIENT"], context_object["WORKSPACE_ID"], resource_cls, resource
    )
    assert result.exit_code == 0


# @pytest.mark.parametrize(
#     "command,resource_id",
#     [
#         (commands.destination, "my_resource_id"),
#     ],
# )
# def test_destination(mocker, context_object, command, resource_id):
#     runner = CliRunner()
#     mocker.patch.object(commands, "Destination", mocker.Mock())
#     mock_renderer = commands.Destination.return_value
#     mock_renderer.get_remote_resource.return_value = '{"hello": "world"}'
#     result = runner.invoke(command, [resource_id], obj=context_object)
#     assert result.exit_code == 0
#     commands.Destination.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], resource_id)


# @pytest.mark.parametrize(
#     "command,resource_id",
#     [
#         (commands.connection, "my_resource_id"),
#     ],
# )
# def test_connection(mocker, context_object, command, resource_id):
#     runner = CliRunner()
#     mocker.patch.object(commands, "Connection", mocker.Mock())
#     mock_renderer = commands.Connection.return_value
#     mock_renderer.get_remote_resource.return_value = '{"hello": "world"}'
#     result = runner.invoke(command, [resource_id], obj=context_object)
#     assert result.exit_code == 0
#     commands.Connection.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], resource_id)
