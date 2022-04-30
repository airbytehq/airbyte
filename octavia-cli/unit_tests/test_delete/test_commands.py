#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from click.testing import CliRunner
from octavia_cli.delete import commands


@pytest.fixture
def context_object(mock_api_client, mock_telemetry_client):
    return {
        "API_CLIENT": mock_api_client,
        "WORKSPACE_ID": "my_workspace_id",
        "TELEMETRY_CLIENT": mock_telemetry_client,
        "SOURCE_CONNECTOR_DEFINITION": "my_source_conn_def",
    }


@pytest.fixture
def source_definition_id():
    return "Bob"


@pytest.fixture
def source_id():
    return "Bob"


@pytest.fixture
def destination_definition_id():
    return "Alice"


@pytest.fixture
def destination_id():
    return "Alice"


@pytest.fixture
def connection_id():
    return "MyConnection"


def test_available_commands():
    assert commands.AVAILABLE_COMMANDS == [commands.connectors, commands.workspace]


def test_commands_in_list_group():
    delete_commands = commands._delete.commands.values()
    for command in commands.AVAILABLE_COMMANDS:
        assert command in delete_commands


def test_source_connector(mocker, context_object, source_definition_id):
    mocker.patch.object(commands, "SourceConnectorsDefinitions", mocker.Mock(return_value="SourceConnectorsDefinitionsRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.sources_connectors, args=["--sourceDefinitionId", source_definition_id], obj=context_object)
    commands.SourceConnectorsDefinitions.assert_called_with(context_object["API_CLIENT"], source_definition_id)
    assert result.output == "SourceConnectorsDefinitionsRepr\n"


def test_destination_connector(mocker, context_object, destination_definition_id):
    mocker.patch.object(commands, "DestinationConnectorsDefinitions", mocker.Mock(return_value="DestinationConnectorsDefinitionsRepr"))
    runner = CliRunner()
    result = runner.invoke(
        commands.destinations_connectors, args=["--destinationDefinitionId", destination_definition_id], obj=context_object
    )
    commands.DestinationConnectorsDefinitions.assert_called_with(context_object["API_CLIENT"], destination_definition_id)
    assert result.output == "DestinationConnectorsDefinitionsRepr\n"


def test_sources(mocker, context_object, source_id):
    mocker.patch.object(commands, "Sources", mocker.Mock(return_value="SourcesRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.sources, args=["--sourceId", source_id], obj=context_object)
    commands.Sources.assert_called_with(context_object["API_CLIENT"], source_id)
    assert result.output == "SourcesRepr\n"


def test_destinations(mocker, context_object, destination_id):
    mocker.patch.object(commands, "Destinations", mocker.Mock(return_value="DestinationsRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.destinations, args=["--destinationId", destination_id], obj=context_object)
    commands.Destinations.assert_called_with(context_object["API_CLIENT"], destination_id)
    assert result.output == "DestinationsRepr\n"


def test_connectionss(mocker, context_object, connection_id):
    mocker.patch.object(commands, "Connections", mocker.Mock(return_value="ConnectionsRepr"))
    runner = CliRunner()
    result = runner.invoke(commands.connections, args=["--connectionId", connection_id], obj=context_object)
    commands.Connections.assert_called_with(context_object["API_CLIENT"], connection_id)
    assert result.output == "ConnectionsRepr\n"
