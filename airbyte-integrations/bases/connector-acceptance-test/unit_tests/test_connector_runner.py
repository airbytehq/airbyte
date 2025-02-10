#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
from pathlib import Path

import pytest
from connector_acceptance_test.utils import connector_runner

from airbyte_protocol.models import (
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    OrchestratorType,
)
from airbyte_protocol.models import Type as AirbyteMessageType


pytestmark = pytest.mark.anyio


class TestContainerRunner:
    @pytest.fixture
    def dev_image_name(self):
        return "airbyte/source-faker:dev"

    @pytest.fixture
    def released_image_name(self):
        return "airbyte/source-faker:latest"

    async def test_get_container_env_variable_value(self, source_faker_container):
        runner = connector_runner.ConnectorRunner(source_faker_container, custom_environment_variables={"FOO": "BAR"})
        assert await runner.get_container_env_variable_value("FOO") == "BAR"

    @pytest.mark.parametrize("deployment_mode", ["oss", "cloud"])
    async def test_set_deployment_mode_env(self, source_faker_container, deployment_mode):
        runner = connector_runner.ConnectorRunner(source_faker_container, deployment_mode=deployment_mode)
        assert await runner.get_container_env_variable_value("DEPLOYMENT_MODE") == deployment_mode.upper()

    def test_parse_airbyte_messages_from_command_output(self, mocker, tmp_path):
        old_configuration_path = tmp_path / "config.json"
        new_configuration = {"field_a": "new_value_a"}
        mock_logging = mocker.MagicMock()
        mocker.patch.object(connector_runner, "logging", mock_logging)
        mocker.patch.object(connector_runner, "docker")
        raw_command_output = "\n".join(
            [
                AirbyteMessage(
                    type=AirbyteMessageType.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"foo": "bar"}, emitted_at=1.0)
                ).json(exclude_unset=False),
                AirbyteMessage(
                    type=AirbyteMessageType.CONTROL,
                    control=AirbyteControlMessage(
                        type=OrchestratorType.CONNECTOR_CONFIG,
                        emitted_at=1.0,
                        connectorConfig=AirbyteControlConnectorConfigMessage(config=new_configuration),
                    ),
                ).json(exclude_unset=False),
                "invalid message",
            ]
        )

        mocker.patch.object(connector_runner.ConnectorRunner, "_persist_new_configuration")
        runner = connector_runner.ConnectorRunner(
            mocker.Mock(),
            connector_configuration_path=old_configuration_path,
        )
        runner.parse_airbyte_messages_from_command_output(raw_command_output)
        runner._persist_new_configuration.assert_called_once_with(new_configuration, 1)
        mock_logging.warning.assert_called_once()

    @pytest.mark.parametrize(
        "pass_configuration_path, old_configuration, new_configuration, new_configuration_emitted_at, expect_new_configuration",
        [
            pytest.param(
                True,
                {"field_a": "value_a"},
                {"field_a": "value_a"},
                1,
                False,
                id="Config unchanged: No new configuration persisted",
            ),
            pytest.param(
                True, {"field_a": "value_a"}, {"field_a": "new_value_a"}, 1, True, id="Config changed: New configuration persisted"
            ),
            pytest.param(
                False,
                {"field_a": "value_a"},
                {"field_a": "new_value_a"},
                1,
                False,
                id="Config changed but persistence is disable: New configuration not persisted",
            ),
        ],
    )
    def test_persist_new_configuration(
        self,
        mocker,
        tmp_path,
        pass_configuration_path,
        old_configuration,
        new_configuration,
        new_configuration_emitted_at,
        expect_new_configuration,
    ):
        if pass_configuration_path:
            old_configuration_path = tmp_path / "config.json"
            with open(old_configuration_path, "w") as old_configuration_file:
                json.dump(old_configuration, old_configuration_file)
        else:
            old_configuration_path = None

        runner = connector_runner.ConnectorRunner(mocker.MagicMock(), connector_configuration_path=old_configuration_path)
        new_configuration_path = runner._persist_new_configuration(new_configuration, new_configuration_emitted_at)
        if not expect_new_configuration:
            assert new_configuration_path is None
        else:
            assert new_configuration_path == tmp_path / "updated_configurations" / f"config|{new_configuration_emitted_at}.json"


async def test_get_connector_container(mocker):
    dagger_client = mocker.AsyncMock()
    os.environ["CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH"] = "test_tarball_path"

    # Mock the functions called within get_connector_container
    mocker.patch.object(connector_runner, "get_container_from_id", new=mocker.AsyncMock())
    mocker.patch.object(connector_runner, "get_container_from_tarball_path", new=mocker.AsyncMock())
    mocker.patch.object(connector_runner, "get_container_from_local_image", new=mocker.AsyncMock())
    mocker.patch.object(connector_runner, "get_container_from_dockerhub_image", new=mocker.AsyncMock())

    # Test the case when the CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH is set
    await connector_runner.get_connector_container(dagger_client, "test_image:tag")
    connector_runner.get_container_from_tarball_path.assert_called_with(dagger_client, Path("test_tarball_path"))

    # Test the case when the CONNECTOR_CONTAINER_ID is set
    Path("/tmp/container_id.txt").write_text("test_container_id")
    await connector_runner.get_connector_container(dagger_client, "test_image:tag")
    connector_runner.get_container_from_id.assert_called_with(dagger_client, "test_container_id")
    Path("/tmp/container_id.txt").unlink()

    # Test the case when none of the environment variables are set
    os.environ.pop("CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH")
    await connector_runner.get_connector_container(dagger_client, "test_image:tag")
    connector_runner.get_container_from_local_image.assert_called_with(dagger_client, "test_image:tag")

    # Test the case when all previous attempts fail
    connector_runner.get_container_from_local_image.return_value = None
    await connector_runner.get_connector_container(dagger_client, "test_image:tag")
    connector_runner.get_container_from_dockerhub_image.assert_called_with(dagger_client, "test_image:tag")
