#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest import mock

from click.testing import CliRunner
from octavia_cli.list import commands


def test_available_commands():
    assert commands.AVAILABLE_COMMANDS == [commands.connectors]


def test_commands_in_list_group():
    list_commands = commands._list.commands.values()
    for command in commands.AVAILABLE_COMMANDS:
        assert command in list_commands


@mock.patch("octavia_cli.list.commands.SourceDefinitions")
def test_connectors_sources(mock_source_definitions, mocker):
    mock_source_definitions.return_value = "SourceDefinitionsRepr"
    context_object = {"API_CLIENT": mocker.Mock()}
    runner = CliRunner()
    result = runner.invoke((commands.sources), obj=context_object)
    mock_source_definitions.assert_called_with(context_object["API_CLIENT"])
    assert result.output == "SourceDefinitionsRepr\n"


@mock.patch("octavia_cli.list.commands.DestinationDefinitions")
def test_connectors_destinations(mock_destination_definitions, mocker):
    mock_destination_definitions.return_value = "DestinationDefinitionsRepr"
    context_object = {"API_CLIENT": mocker.Mock()}
    runner = CliRunner()
    result = runner.invoke((commands.destinations), obj=context_object)
    mock_destination_definitions.assert_called_with(context_object["API_CLIENT"])
    assert result.output == "DestinationDefinitionsRepr\n"
