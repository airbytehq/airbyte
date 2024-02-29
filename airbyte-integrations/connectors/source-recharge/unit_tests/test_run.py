# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from argparse import Namespace
from typing import Union
from unittest.mock import MagicMock

import pytest
from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.models import (
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteMessage,
    ConnectorSpecification,
    OrchestratorType,
    Type,
)
from airbyte_cdk.sources import Source


class MockSource(Source):
    def read(self, **kwargs):
        pass

    def discover(self, **kwargs):
        pass

    def check(self, **kwargs):
        pass

    @property
    def message_repository(self):
        pass


@pytest.fixture
def entrypoint(mocker) -> AirbyteEntrypoint:
    message_repository = MagicMock()
    message_repository.consume_queue.side_effect = [[message for message in [MESSAGE_FROM_REPOSITORY]], [], []]
    mocker.patch.object(MockSource, "message_repository", new_callable=mocker.PropertyMock, return_value=message_repository)
    return AirbyteEntrypoint(MockSource())


MESSAGE_FROM_REPOSITORY = AirbyteMessage(
    type=Type.CONTROL,
    control=AirbyteControlMessage(
        type=OrchestratorType.CONNECTOR_CONFIG,
        emitted_at=10,
        connectorConfig=AirbyteControlConnectorConfigMessage(
            config={"any config": "a config value"},
        ),
    ),
)


def _wrap_message(submessage: Union[ConnectorSpecification]) -> str:
    if isinstance(submessage, ConnectorSpecification):
        message = AirbyteMessage(type=Type.SPEC, spec=submessage)
    else:
        raise Exception(f"Unknown message type: {submessage}")
    return message.json(exclude_unset=True)


def test_run_spec(entrypoint: AirbyteEntrypoint, mocker):
    parsed_args = Namespace(command="spec")
    expected = ConnectorSpecification(connectionSpecification={"test": "test"})
    mocker.patch.object(MockSource, "spec", return_value=expected)
    messages = list(entrypoint.run(parsed_args))
    assert [MESSAGE_FROM_REPOSITORY.json(exclude_unset=True), _wrap_message(expected)] == messages
