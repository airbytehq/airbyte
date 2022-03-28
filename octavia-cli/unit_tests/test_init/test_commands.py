#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from click.testing import CliRunner
from octavia_cli.init import commands


def test_directories_to_create():
    assert commands.DIRECTORIES_TO_CREATE == {"connections", "destinations", "sources"}


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


def test_init(mocker):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=(["dir_a", "dir_b"], [])))
    result = runner.invoke(commands.init)
    assert result.exit_code == 0
    assert result.output == "🔨 - Initializing the project.\n✅ - Created the following directories: dir_a, dir_b.\n"


def test_init_some_existing_directories(mocker):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=(["dir_a"], ["dir_b"])))
    result = runner.invoke(commands.init)
    assert result.exit_code == 0
    assert (
        result.output
        == "🔨 - Initializing the project.\n✅ - Created the following directories: dir_a.\n❓ - Already existing directories: dir_b.\n"
    )


def test_init_all_existing_directories(mocker):
    runner = CliRunner()
    mocker.patch.object(commands, "create_directories", mocker.Mock(return_value=([], ["dir_a", "dir_b"])))
    result = runner.invoke(commands.init)
    assert result.exit_code == 0
    assert result.output == "🔨 - Initializing the project.\n❓ - Already existing directories: dir_a, dir_b.\n"
