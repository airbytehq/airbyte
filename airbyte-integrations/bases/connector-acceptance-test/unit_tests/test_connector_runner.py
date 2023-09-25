#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os

import pytest
from airbyte_protocol.models import (
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    OrchestratorType,
)
from airbyte_protocol.models import Type as AirbyteMessageType
from connector_acceptance_test.utils import connector_runner

pytestmark = pytest.mark.anyio


class TestContainerRunner:
    @pytest.fixture
    def dev_image_name(self):
        return "airbyte/source-faker:dev"

    @pytest.fixture
    def released_image_name(self):
        return "airbyte/source-faker:latest"

    @pytest.fixture()
    async def local_tar_image(self, dagger_client, tmpdir, released_image_name):
        local_image_tar_path = str(tmpdir / "local_image.tar")
        await dagger_client.container().from_(released_image_name).export(local_image_tar_path)
        os.environ["CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH"] = local_image_tar_path
        yield local_image_tar_path
        os.environ.pop("CONNECTOR_UNDER_TEST_IMAGE_TAR_PATH")

    async def test_load_container_from_tar(self, dagger_client, dev_image_name, local_tar_image):
        runner = connector_runner.ConnectorRunner(dev_image_name, dagger_client)
        await runner.load_container()
        assert await runner._connector_under_test_container.with_exec(["spec"])

    async def test_load_container_from_released_connector(self, dagger_client, released_image_name):
        runner = connector_runner.ConnectorRunner(released_image_name, dagger_client)
        await runner.load_container()
        assert await runner._connector_under_test_container.with_exec(["spec"])

    async def test_get_container_env_variable_value(self, dagger_client, dev_image_name, local_tar_image):
        runner = connector_runner.ConnectorRunner(dev_image_name, dagger_client, custom_environment_variables={"FOO": "BAR"})
        assert await runner.get_container_env_variable_value("FOO") == "BAR"

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
            "source-test:dev",
            mocker.Mock(),
            connector_configuration_path=old_configuration_path,
            custom_environment_variables={"foo": "bar"},
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
        mocker.patch.object(connector_runner, "docker")
        runner = connector_runner.ConnectorRunner("source-test:dev", mocker.MagicMock(), old_configuration_path)
        new_configuration_path = runner._persist_new_configuration(new_configuration, new_configuration_emitted_at)
        if not expect_new_configuration:
            assert new_configuration_path is None
        else:
            assert new_configuration_path == tmp_path / "updated_configurations" / f"config|{new_configuration_emitted_at}.json"
