#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from click.testing import CliRunner
from octavia_cli.apply.resources import NonExistingResourceError
from octavia_cli.generate import commands


@pytest.fixture
def context_object(mock_api_client, mock_telemetry_client):
    return {"PROJECT_IS_INITIALIZED": True, "API_CLIENT": mock_api_client, "WORKSPACE_ID": "foo", "TELEMETRY_CLIENT": mock_telemetry_client}


def test_generate_initialized(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "definitions")
    mocker.patch.object(commands, "ConnectorSpecificationRenderer", mocker.Mock())
    mock_renderer = commands.ConnectorSpecificationRenderer.return_value
    mock_renderer.write_yaml.return_value = "expected_output_path"
    result = runner.invoke(commands.generate, ["source", "uuid", "my_source"], obj=context_object)
    assert result.exit_code == 0


def test_generate_not_initialized(context_object):
    runner = CliRunner()
    context_object["PROJECT_IS_INITIALIZED"] = False
    result = runner.invoke(commands.generate, ["source", "uuid", "my_source"], obj=context_object)
    assert result.exit_code == 1

    assert result.output == "Error: Your octavia project is not initialized, please run 'octavia init' before running this command.\n"


def test_invalid_definition_type(context_object):
    runner = CliRunner()
    result = runner.invoke(commands.generate, ["random_definition", "uuid", "my_source"], obj=context_object)
    assert result.exit_code == 2


@pytest.mark.parametrize(
    "command,resource_name,definition_type",
    [
        (commands.source, "my_source", "source"),
        (commands.destination, "my_destination", "destination"),
    ],
)
def test_generate_source_or_destination(mocker, context_object, command, resource_name, definition_type):
    runner = CliRunner()
    mocker.patch.object(commands, "definitions")
    mocker.patch.object(commands, "ConnectorSpecificationRenderer", mocker.Mock())
    mock_renderer = commands.ConnectorSpecificationRenderer.return_value
    mock_renderer.write_yaml.return_value = "expected_output_path"
    result = runner.invoke(command, ["uuid", resource_name], obj=context_object)
    assert result.exit_code == 0
    assert result.output == f"✅ - Created the {definition_type} template for {resource_name} in expected_output_path.\n"
    commands.definitions.factory.assert_called_with(definition_type, context_object["API_CLIENT"], context_object["WORKSPACE_ID"], "uuid")
    commands.ConnectorSpecificationRenderer.assert_called_with(resource_name, commands.definitions.factory.return_value)
    mock_renderer.write_yaml.assert_called_with(project_path=".")


@pytest.fixture
def tmp_source_path(tmp_path):
    source_path = tmp_path / "my_source.yaml"
    source_path.write_text("foo")
    return source_path


@pytest.fixture
def tmp_destination_path(tmp_path):
    destination_path = tmp_path / "my_destination.yaml"
    destination_path.write_text("foo")
    return destination_path


@pytest.mark.parametrize(
    "source_created,destination_created",
    [(True, True), (False, True), (True, False), (False, False)],
)
def test_generate_connection(mocker, context_object, tmp_source_path, tmp_destination_path, source_created, destination_created):
    runner = CliRunner()
    mock_source = mocker.Mock(was_created=source_created)
    mock_destination = mocker.Mock(was_created=destination_created)

    mock_resource_factory = mocker.Mock(side_effect=[mock_source, mock_destination])
    mocker.patch.object(
        commands, "resources", mocker.Mock(factory=mock_resource_factory, NonExistingResourceError=NonExistingResourceError)
    )
    mocker.patch.object(commands, "ConnectionRenderer", mocker.Mock())
    mock_renderer = commands.ConnectionRenderer.return_value
    mock_renderer.write_yaml.return_value = "expected_output_path"
    cli_input = ["my_new_connection", "--source", tmp_source_path, "--destination", tmp_destination_path]
    result = runner.invoke(commands.connection, cli_input, obj=context_object)
    if source_created and destination_created:
        assert result.exit_code == 0
        assert result.output == "✅ - Created the connection template for my_new_connection in expected_output_path.\n"
        commands.resources.factory.assert_has_calls(
            [
                mocker.call(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], tmp_source_path),
                mocker.call(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], tmp_destination_path),
            ]
        )
        commands.ConnectionRenderer.assert_called_with("my_new_connection", mock_source, mock_destination)
        mock_renderer.write_yaml.assert_called_with(project_path=".")
    elif not source_created:
        assert (
            result.output
            == f"Error: The source defined at {tmp_source_path} does not exists. Please run octavia apply before creating this connection.\n"
        )
        assert result.exit_code == 1
    elif not destination_created:
        assert (
            result.output
            == f"Error: The destination defined at {tmp_destination_path} does not exists. Please run octavia apply before creating this connection.\n"
        )
        assert result.exit_code == 1
