#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import click
import pytest
from octavia_cli import telemetry


def test_build_user_agent():
    ua = telemetry.build_user_agent("my_octavia_version", "my_workspace_id")
    assert ua == "octavia-cli/my_octavia_version/my_workspace_id"


class TestTelemetryClient:
    @pytest.mark.parametrize("send_data", [True, False])
    def test_init(self, mocker, send_data):
        assert isinstance(telemetry.TelemetryClient.DEV_WRITE_KEY, str)
        assert isinstance(telemetry.TelemetryClient.PROD_WRITE_KEY, str)
        mocker.patch.object(telemetry.TelemetryClient, "write_key", "my_write_key")
        mocker.patch.object(telemetry.analytics, "Client")
        telemetry_client = telemetry.TelemetryClient(send_data)
        assert telemetry_client.segment_client == telemetry.analytics.Client.return_value
        telemetry.analytics.Client.assert_called_with("my_write_key", send=send_data)

    @pytest.fixture
    def telemetry_client(self, mocker):
        mocker.patch.object(telemetry.analytics, "Client")
        return telemetry.TelemetryClient(True)

    @pytest.mark.parametrize("octavia_env", ["dev", "foo", "bar", None])
    def test_write_key(self, mocker, telemetry_client, octavia_env):
        mocker.patch.object(telemetry.os, "getenv", mocker.Mock(return_value=octavia_env))
        if octavia_env == "dev":
            assert telemetry_client.write_key == telemetry_client.DEV_WRITE_KEY
        else:
            assert telemetry_client.write_key == telemetry_client.PROD_WRITE_KEY

    @pytest.mark.parametrize("extra_info_name", ["foo", None])
    def test__create_command_name_multi_contexts(self, mocker, telemetry_client, extra_info_name):
        grand_parent_ctx = click.Context(mocker.Mock(), None, "grand_parent_command")
        parent_ctx = click.Context(mocker.Mock(), grand_parent_ctx, "parent_command")
        ctx = click.Context(mocker.Mock(), parent_ctx, "child_command")
        command_name = telemetry_client._create_command_name(ctx, extra_info_name=extra_info_name)
        if extra_info_name:
            assert command_name == f"grand_parent_command parent_command child_command {extra_info_name}"
        else:
            assert command_name == "grand_parent_command parent_command child_command"

    @pytest.mark.parametrize("extra_info_name", ["foo", None])
    def test__create_command_name_single_context(self, mocker, telemetry_client, extra_info_name):
        ctx = click.Context(mocker.Mock(), None, "child_command")
        command_name = telemetry_client._create_command_name(ctx, extra_info_name=extra_info_name)
        if extra_info_name:
            assert command_name == f"child_command {extra_info_name}"
        else:
            assert command_name == "child_command"

    @pytest.mark.parametrize(
        "workspace_id,airbyte_role,project_is_initialized,octavia_version,error, expected_success, expected_error_type",
        [
            (None, None, None, None, None, True, None),
            ("my_workspace_id", "my_airbyte_role", True, "0.1.0", None, True, None),
            ("my_workspace_id", "my_airbyte_role", False, "0.1.0", None, True, None),
            ("my_workspace_id", "my_airbyte_role", False, "0.1.0", AttributeError(), False, "AttributeError"),
            ("my_workspace_id", "my_airbyte_role", True, "0.1.0", AttributeError(), False, "AttributeError"),
            (None, None, True, "0.1.0", AttributeError(), False, "AttributeError"),
        ],
    )
    def test_send_command_telemetry(
        self,
        mocker,
        telemetry_client,
        workspace_id,
        airbyte_role,
        project_is_initialized,
        octavia_version,
        error,
        expected_success,
        expected_error_type,
    ):
        extra_info_name = "foo"
        mocker.patch.object(telemetry.os, "getenv", mocker.Mock(return_value=airbyte_role))
        mocker.patch.object(telemetry.uuid, "uuid1", mocker.Mock(return_value="MY_UUID"))
        expected_user_id = workspace_id if workspace_id is not None else None
        expected_anonymous_id = "MY_UUID" if workspace_id is None else None
        mock_ctx = mocker.Mock(
            obj={
                "OCTAVIA_VERSION": octavia_version,
                "PROJECT_IS_INITIALIZED": project_is_initialized,
                "WORKSPACE_ID": workspace_id,
            }
        )
        expected_segment_context = {"app": {"name": "octavia-cli", "version": octavia_version}}
        expected_properties = {
            "success": expected_success,
            "error_type": expected_error_type,
            "project_is_initialized": project_is_initialized,
            "airbyte_role": airbyte_role,
        }
        telemetry_client.segment_client = mocker.Mock()
        telemetry_client._create_command_name = mocker.Mock(return_value="my_command")
        telemetry_client.send_command_telemetry(mock_ctx, error=error, extra_info_name=extra_info_name)
        telemetry_client._create_command_name.assert_called_with(mock_ctx, extra_info_name)
        telemetry_client.segment_client.track.assert_called_with(
            user_id=expected_user_id,
            anonymous_id=expected_anonymous_id,
            event="my_command",
            properties=expected_properties,
            context=expected_segment_context,
        )
