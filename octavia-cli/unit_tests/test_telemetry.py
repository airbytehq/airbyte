#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import click
import pytest
from octavia_cli import telemetry


def test_build_user_agent():
    ua = telemetry.build_user_agent("my_octavia_version")
    assert ua == "octavia-cli/my_octavia_version"


class TestTelemetryClient:
    @pytest.mark.parametrize("send_data", [True, False])
    def test_init(self, mocker, send_data):
        assert isinstance(telemetry.TelemetryClient.WRITE_KEY, str)
        mocker.patch.object(telemetry.TelemetryClient, "write_key", "my_write_key")
        mocker.patch.object(telemetry.analytics, "Client")
        telemetry_client = telemetry.TelemetryClient(send_data)
        assert telemetry_client.segment_client == telemetry.analytics.Client.return_value
        telemetry.analytics.Client.assert_called_with("my_write_key", send=send_data)

    @pytest.fixture
    def telemetry_client(self, mocker):
        mocker.patch.object(telemetry.analytics, "Client")
        return telemetry.TelemetryClient(True)

    @pytest.mark.parametrize("octavia_custom_write_key", ["my_custom_write_key", None])
    def test_write_key(self, mocker, telemetry_client, octavia_custom_write_key):
        mocker.patch.object(telemetry.os, "getenv", mocker.Mock(return_value=octavia_custom_write_key))
        assert telemetry_client.write_key == telemetry.os.getenv.return_value
        telemetry.os.getenv.assert_called_with("OCTAVIA_TELEMETRY_WRITE_KEY", telemetry_client.WRITE_KEY)

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
        "workspace_id, anonymous_data_collection, airbyte_role, project_is_initialized, octavia_version, error, expected_success, expected_error_type, is_help",
        [
            (None, None, None, None, None, None, True, None, False),
            (None, None, None, None, None, Exception(), False, "Exception", False),
            (None, None, None, None, None, AttributeError(), False, "AttributeError", False),
            (None, True, None, None, None, None, True, None, False),
            (None, True, None, None, None, Exception(), False, "Exception", False),
            (None, True, None, None, None, AttributeError(), False, "AttributeError", False),
            ("my_workspace_id", False, None, None, None, None, True, None, False),
            ("my_workspace_id", False, None, None, None, Exception(), False, "Exception", False),
            ("my_workspace_id", True, None, None, None, None, True, None, False),
            ("my_workspace_id", True, None, None, None, Exception(), False, "Exception", False),
            ("my_workspace_id", True, "airbyter", None, None, None, True, None, False),
            ("my_workspace_id", True, "non_airbyter", None, None, Exception(), False, "Exception", False),
            ("my_workspace_id", True, "airbyter", True, None, None, True, None, False),
            ("my_workspace_id", True, "non_airbyter", False, None, Exception(), False, "Exception", False),
            ("my_workspace_id", True, "airbyter", True, None, None, True, None, False),
            ("my_workspace_id", True, "non_airbyter", False, "0.1.0", Exception(), False, "Exception", False),
            ("my_workspace_id", True, "non_airbyter", False, "0.1.0", None, True, None, False),
            ("my_workspace_id", True, "non_airbyter", False, "0.1.0", None, True, None, True),
        ],
    )
    def test_send_command_telemetry(
        self,
        mocker,
        telemetry_client,
        workspace_id,
        anonymous_data_collection,
        airbyte_role,
        project_is_initialized,
        octavia_version,
        error,
        expected_success,
        expected_error_type,
        is_help,
    ):
        extra_info_name = "foo"
        mocker.patch.object(telemetry.os, "getenv", mocker.Mock(return_value=airbyte_role))
        mocker.patch.object(telemetry.uuid, "uuid1", mocker.Mock(return_value="MY_UUID"))
        expected_user_id = workspace_id if workspace_id is not None and anonymous_data_collection is False else None
        expected_anonymous_id = "MY_UUID" if expected_user_id is None else None
        mock_ctx = mocker.Mock(
            obj={
                "OCTAVIA_VERSION": octavia_version,
                "PROJECT_IS_INITIALIZED": project_is_initialized,
                "WORKSPACE_ID": workspace_id,
                "ANONYMOUS_DATA_COLLECTION": anonymous_data_collection,
            }
        )
        expected_segment_context = {"app": {"name": "octavia-cli", "version": octavia_version}}
        expected_properties = {
            "success": expected_success,
            "is_help": is_help,
            "error_type": expected_error_type,
            "project_is_initialized": project_is_initialized,
            "airbyter": airbyte_role == "airbyter",
        }
        telemetry_client.segment_client = mocker.Mock()
        telemetry_client._create_command_name = mocker.Mock(return_value="my_command")

        telemetry_client.send_command_telemetry(mock_ctx, error=error, extra_info_name=extra_info_name, is_help=is_help)
        telemetry_client._create_command_name.assert_called_with(mock_ctx, extra_info_name=extra_info_name)
        telemetry_client.segment_client.track.assert_called_with(
            user_id=expected_user_id,
            anonymous_id=expected_anonymous_id,
            event="my_command",
            properties=expected_properties,
            context=expected_segment_context,
        )
