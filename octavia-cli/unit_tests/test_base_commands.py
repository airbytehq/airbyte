#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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

    def test_make_context_error(self, mocker, octavia_command, mock_telemetry_client):
        mock_parent_ctx = mocker.Mock(obj={"TELEMETRY_CLIENT": mock_telemetry_client})
        error = Exception()
        parent_make_context = mocker.Mock(side_effect=error)
        mocker.patch.object(click.Command, "make_context", parent_make_context)
        with pytest.raises(Exception):
            octavia_command.make_context("my_info_name", ["arg1", "arg2"], parent=mock_parent_ctx, foo="foo", bar="bar")
            mock_telemetry_client.send_command_telemetry.assert_called_with(mock_parent_ctx, error=error, extra_info_name="my_info_name")

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
