#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import click
import pytest
from octavia_cli import base_commands


class TestOctaviaCommand:
    @pytest.fixture
    def octavia_command(self):
        octavia_command = base_commands.OctaviaCommand("test_command")
        assert isinstance(octavia_command, click.Command)
        return octavia_command

    def test_make_context(self, mocker, octavia_command):
        mock_parent_ctx = mocker.Mock()
        parent_make_context = mocker.Mock()
        mocker.patch.object(click.Command, "make_context", parent_make_context)
        made_context = octavia_command.make_context("my_info_name", ["arg1", "arg2"], parent=mock_parent_ctx, foo="foo", bar="bar")
        parent_make_context.assert_called_with("my_info_name", ["arg1", "arg2"], mock_parent_ctx, foo="foo", bar="bar")
        assert made_context == parent_make_context.return_value

    @pytest.mark.parametrize("error", [Exception(), click.exceptions.Exit(0), click.exceptions.Exit(1)])
    def test_make_context_error(self, mocker, octavia_command, mock_telemetry_client, error):
        mock_parent_ctx = mocker.Mock(obj={"TELEMETRY_CLIENT": mock_telemetry_client})
        parent_make_context = mocker.Mock(side_effect=error)
        mocker.patch.object(click.Command, "make_context", parent_make_context)
        with pytest.raises(type(error)):
            octavia_command.make_context("my_info_name", ["arg1", "arg2"], parent=mock_parent_ctx, foo="foo", bar="bar")
            if isinstance(error, click.exceptions.Exit) and error.exit_code == 0:
                mock_telemetry_client.send_command_telemetry.assert_called_with(
                    mock_parent_ctx, extra_info_name="my_info_name", is_help=True
                )
            else:
                mock_telemetry_client.send_command_telemetry.assert_called_with(
                    mock_parent_ctx, error=error, extra_info_name="my_info_name"
                )

    def test_invoke(self, mocker, octavia_command, mock_telemetry_client):
        mock_ctx = mocker.Mock(obj={"TELEMETRY_CLIENT": mock_telemetry_client})
        parent_invoke = mocker.Mock()
        mocker.patch.object(click.Command, "invoke", parent_invoke)
        result = octavia_command.invoke(mock_ctx)
        parent_invoke.assert_called_with(mock_ctx)
        mock_telemetry_client.send_command_telemetry.assert_called_with(mock_ctx)
        assert result == parent_invoke.return_value

    def test_invoke_error(self, mocker, octavia_command, mock_telemetry_client):
        mock_ctx = mocker.Mock(obj={"TELEMETRY_CLIENT": mock_telemetry_client})
        error = Exception()
        parent_invoke = mocker.Mock(side_effect=error)
        mocker.patch.object(click.Command, "invoke", parent_invoke)
        with pytest.raises(Exception):
            octavia_command.invoke(mock_ctx)
            mock_telemetry_client.send_command_telemetry.assert_called_with(mock_ctx, error=error)
