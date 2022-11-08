#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from click.testing import CliRunner
from octavia_cli.list import commands


@pytest.fixture
def context_object(mock_api_client, mock_telemetry_client):
    return {"API_CLIENT": mock_api_client, "WORKSPACE_ID": "my_workspace_id", "TELEMETRY_CLIENT": mock_telemetry_client}


def test_available_commands():
    assert commands.AVAILABLE_COMMANDS == [commands.connectors, commands.workspace]


def test_commands_in_list_group():
    list_commands = commands._list.commands.values()
    for command in commands.AVAILABLE_COMMANDS:
        assert command in list_commands


def test_connectors_sources(mocker, context_object):
    mocker.patch.object(commands, "SourceConnectorsDefinitions", mocker.Mock(return_value="SourceConnectorsDefinitionsRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.sources_connectors, obj=context_object)
    commands.SourceConnectorsDefinitions.assert_called_with(context_object["API_CLIENT"])
    assert result.output == "SourceConnectorsDefinitionsRepr\n"


def test_connectors_destinations(mocker, context_object):
    mocker.patch.object(commands, "DestinationConnectorsDefinitions", mocker.Mock(return_value="DestinationConnectorsDefinitionsRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.destinations_connectors, obj=context_object)
    commands.DestinationConnectorsDefinitions.assert_called_with(context_object["API_CLIENT"])
    assert result.output == "DestinationConnectorsDefinitionsRepr\n"


def test_sources(mocker, context_object):
    mocker.patch.object(commands, "Sources", mocker.Mock(return_value="SourcesRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.sources, obj=context_object)
    commands.Sources.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"])
    assert result.output == "SourcesRepr\n"


def test_destinations(mocker, context_object):
    mocker.patch.object(commands, "Destinations", mocker.Mock(return_value="DestinationsRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.destinations, obj=context_object)
    commands.Destinations.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"])
    assert result.output == "DestinationsRepr\n"


def test_connections(mocker, context_object):
    mocker.patch.object(commands, "Connections", mocker.Mock(return_value="ConnectionsRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.connections, obj=context_object)
    commands.Connections.assert_called_with(context_object["API_CLIENT"], context_object["WORKSPACE_ID"])
    assert result.output == "ConnectionsRepr\n"
