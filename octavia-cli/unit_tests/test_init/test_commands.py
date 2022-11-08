#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import mock_open, patch

import pytest
from click.testing import CliRunner
from octavia_cli.init import commands
from octavia_cli.init.commands import create_api_headers_configuration_file


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
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=True))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert (
        result.output
        == "🔨 - Initializing the project.\n✅ - Created the following directories: dir_a, dir_b.\n"
        + f"✅ - Created API HTTP headers file in {commands.API_HTTP_HEADERS_TARGET_PATH}\n"
    )


def test_init_some_existing_directories(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=(["dir_a"], ["dir_b"])))
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=False))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert "Already existing directories: dir_b.\n" in result.output


def test_init_all_existing_directories(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=([], ["dir_a", "dir_b"])))
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=False))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert "Already existing directories: dir_a, dir_b.\n" in result.output


def test_init_when_api_headers_configuration_file_exists(mocker, context_object):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=([], ["dir_a", "dir_b"])))
    mocker.patch.object(commands, "create_api_headers_configuration_file", mocker.Mock(return_value=False))
    result = runner.invoke(commands.init, obj=context_object)
    assert result.exit_code == 0
    assert "API HTTP headers file already exists, skipping." in result.output


@pytest.mark.parametrize("api_http_headers_file_exist", [False, True])
def test_create_init_configuration(mocker, api_http_headers_file_exist):
    mock_path = mocker.Mock(is_file=mocker.Mock(return_value=api_http_headers_file_exist))
    mocker.patch.object(commands, "API_HTTP_HEADERS_TARGET_PATH", mock_path)
    if not api_http_headers_file_exist:
        with patch("builtins.open", mock_open()) as mock_file:
            assert create_api_headers_configuration_file()
            mock_file.assert_called_with(commands.API_HTTP_HEADERS_TARGET_PATH, "w")
            mock_file.return_value.write.assert_called_with(commands.DEFAULT_API_HEADERS_FILE_CONTENT)
    else:
        assert not create_api_headers_configuration_file()
