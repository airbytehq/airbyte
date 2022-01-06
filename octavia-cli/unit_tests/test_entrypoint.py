#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from click.testing import CliRunner
from octavia_cli import entrypoint


def test_octavia():
    runner = CliRunner()
    result = runner.invoke(entrypoint.octavia)
    assert result.exit_code == 0
    assert result.output.startswith("Usage: octavia [OPTIONS] COMMAND [ARGS]...")


def test_commands_in_octavia_group():
    octavia_commands = entrypoint.octavia.commands.values()
    for command in entrypoint.AVAILABLE_COMMANDS:
        assert command in octavia_commands


@pytest.mark.parametrize(
    "command",
    [entrypoint.init, entrypoint.apply, entrypoint.create, entrypoint.delete, entrypoint._import],
)
def test_not_implemented_commands(command):
    runner = CliRunner()
    result = runner.invoke(command)
    assert result.exit_code == 1
    assert result.output.endswith("not yet implemented.\n")


def test_available_commands():
    assert entrypoint.AVAILABLE_COMMANDS == [entrypoint.list_commands._list]
