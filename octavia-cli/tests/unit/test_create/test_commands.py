#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from click.testing import CliRunner
from octavia_cli.create import commands


def test_create_initialized(mocker):
    runner = CliRunner()
    mocker.patch.object(commands, "definitions", mocker.Mock(return_value=(["dir_a", "dir_b"], [])))
    mocker.patch.object(commands, "ConnectionSpecificationRenderer", mocker.Mock())
    mock_renderer = commands.ConnectionSpecificationRenderer.return_value
    mock_renderer.write_yaml.return_value = "expected_output_path"
    context_object = {"PROJECT_IS_INITIALIZED": True, "API_CLIENT": mocker.Mock()}
    result = runner.invoke(commands.create, ["source", "uuid", "my_source"], obj=context_object)
    assert result.exit_code == 0
    assert result.output == "✅ - Created the specification template for my_source in expected_output_path.\n"
    commands.definitions.factory.assert_called_with("source", context_object["API_CLIENT"], "uuid")
    commands.ConnectionSpecificationRenderer.assert_called_with("my_source", commands.definitions.factory.return_value)
    mock_renderer.write_yaml.assert_called_with(project_path=".")


def test_create_not_initialized():
    runner = CliRunner()
    context_object = {"PROJECT_IS_INITIALIZED": False}
    result = runner.invoke(commands.create, ["source", "uuid", "my_source"], obj=context_object)
    assert result.exit_code == 1
    assert result.output == "Error: Your octavia project is not initialized, please run 'octavia init' before running 'octavia create'.\n"


def test_invalid_definition_type():
    runner = CliRunner()
    result = runner.invoke(commands.create, ["random_definition", "uuid", "my_source"])
    assert result.exit_code == 2
