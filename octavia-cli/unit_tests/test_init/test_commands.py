#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import os

import pytest
import yaml
from click.testing import CliRunner
from octavia_cli.init import commands
from octavia_cli.init.commands import create_octavia_env_file, create_api_headers_configuration_file, API_HEADERS_CONFIGURATION_FILE


def test_directories_to_create():
    assert commands.DIRECTORIES_TO_CREATE == {"connections", "destinations", "sources"}


@pytest.fixture
def context_object(mock_telemetry_client):
    return {"TELEMETRY_CLIENT": mock_telemetry_client}


@pytest.mark.parametrize(
    "directories_to_create,mkdir_side_effects,expected_created_directories,expected_not_created_directories",
    [
        (["dir_a", "dir_b"], None, ["dir_a", "dir_b"], []),
        (["dir_a", "dir_b"], FileExistsError(), [], ["dir_a", "dir_b"]),
        (["dir_a", "dir_b"], [None, FileExistsError()], ["dir_a"], ["dir_b"]),
    ],
)
def test_create_directories(
        mocker, directories_to_create, mkdir_side_effects, expected_created_directories, expected_not_created_directories
):
    mocker.patch.object(commands, "os", mocker.Mock(mkdir=mocker.Mock(side_effect=mkdir_side_effects)))
    created_directories, not_created_directories = commands.create_directories(directories_to_create)
    assert created_directories == expected_created_directories
    assert not_created_directories == expected_not_created_directories
    commands.os.mkdir.assert_has_calls([mocker.call(d) for d in directories_to_create])


def test_init(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=(["dir_a", "dir_b"], [])))
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=False))
    mocker.patch.object(commands, "create_octavia_env_file", mocker.Mock(return_value=False))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert result.output == "🔨 - Initializing the project.\n✅ - Created the following directories: dir_a, dir_b.\n" + \
           "❓ - Application headers file already exists, skipping\n"


def test_init_some_existing_directories(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=(["dir_a"], ["dir_b"])))
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=False))
    mocker.patch.object(commands, "create_octavia_env_file", mocker.Mock(return_value=False))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert (
            result.output
            == "🔨 - Initializing the project.\n✅ - Created the following directories: dir_a.\n❓ " +
            "- Already existing directories: dir_b.\n" +
            "❓ - Application headers file already exists, skipping\n"
    )


def test_init_all_existing_directories(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=([], ["dir_a", "dir_b"])))
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=False))
    mocker.patch.object(commands, "create_octavia_env_file", mocker.Mock(return_value=False))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert result.output == "🔨 - Initializing the project.\n❓ - Already existing directories: dir_a, dir_b.\n" + \
        "❓ - Application headers file already exists, skipping\n"


def test_init_when_application_headers_configuration_file_does_not_exists(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=([], ["dir_a", "dir_b"])))
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=True))
    mocker.patch.object(commands, "create_octavia_env_file", mocker.Mock(return_value=False))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert result.output == "🔨 - Initializing the project.\n❓ - Already existing directories: dir_a, dir_b.\n" + \
           "✅ - Created example application headers configuration file api_headers_configuration.yaml\n"


def test_init_when_octavia_env_file_does_not_exists(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=([], ["dir_b"])))
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=True))
    mocker.patch.object(commands, "create_octavia_env_file", mocker.Mock(return_value=True))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert result.output == "🔨 - Initializing the project.\n❓ - Already existing directories: dir_b.\n" + \
           "✅ - Created example application headers configuration file api_headers_configuration.yaml\n" + \
           "✅ - Created env file with api headers configuration file location .octavia\n"


def test_create_init_configuration():
    # file configuration content
    headers = {
        "headers": [
            {"name": "Content-Type", "value": "application/json"}
        ]}

    # when creating api headers configuration file
    create_api_headers_configuration_file()

    # then content should match expected one
    with open(API_HEADERS_CONFIGURATION_FILE) as file:
        assert yaml.safe_load(file) == headers

    if os.path.exists(API_HEADERS_CONFIGURATION_FILE):
        os.remove(API_HEADERS_CONFIGURATION_FILE)


def test_create_octavia_cli_env_variable_file():
    # given env file name and its content
    env_file_name = ".octavia"
    env_var_name = "AIRBYTE_HEADERS_FILE_PATH"
    env_var_value = "api_headers_configuration.yaml"
    env_variables = {env_var_name: env_var_value}

    # when creating env file
    create_octavia_env_file(env_file_name, env_variables)

    # then file content should be as expected

    with open(env_file_name) as file:
        assert file.readlines() == [f"{env_var_name}={env_var_value}"]

    os.remove(env_file_name)
