#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json

import pytest
from airbyte_cdk.models import (
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    OrchestratorType,
)
from airbyte_cdk.models import Type as AirbyteMessageType
from connector_acceptance_test.utils import connector_runner


class TestContainerRunner:
    def test_run_call_persist_configuration(self, mocker, tmp_path):
        old_configuration_path = tmp_path / "config.json"
        new_configuration = {"field_a": "new_value_a"}
        mocker.patch.object(connector_runner, "docker")
        records_reads = [
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
        ]
        mocker.patch.object(connector_runner.ConnectorRunner, "read", mocker.Mock(return_value=records_reads))
        mocker.patch.object(connector_runner.ConnectorRunner, "_persist_new_configuration")
        runner = connector_runner.ConnectorRunner(
            "source-test:dev", tmp_path, connector_configuration_path=old_configuration_path, custom_environment_variables={"foo": "bar"}
        )
        list(runner.run("dummy_cmd"))
        runner._persist_new_configuration.assert_called_once_with(new_configuration, 1)
        runner._client.containers.run.assert_called_once_with(
            image=runner._image,
            command="dummy_cmd",
            volumes={str(tmp_path) + "/run_1/input": {"bind": "/data"}, str(tmp_path) + "/run_1/output": {"bind": "/local", "mode": "rw"}},
            network_mode="host",
            detach=True,
            environment={"foo": "bar"},
        )

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
        runner = connector_runner.ConnectorRunner("source-test:dev", tmp_path, old_configuration_path)
        new_configuration_path = runner._persist_new_configuration(new_configuration, new_configuration_emitted_at)
        if not expect_new_configuration:
            assert new_configuration_path is None
        else:
            assert new_configuration_path == tmp_path / "updated_configurations" / f"config|{new_configuration_emitted_at}.json"
