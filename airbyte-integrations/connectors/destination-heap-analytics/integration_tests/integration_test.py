#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import sys
from datetime import datetime
from io import StringIO
from json import load
from typing import Any, Dict, List
from unittest.mock import MagicMock

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, AirbyteStateMessage, AirbyteStateType, Level, Status, Type
from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteCatalog
from destination_heap_analytics.destination import DestinationHeapAnalytics
from pytest import fixture


class CaptureStdOut(list):
    """
    Captures the stdout messages into the variable list, that could be validated later.
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout


@fixture(scope="module")
def config_events() -> Dict[str, str]:
    with open(
        "sample_files/config-events.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def configured_catalog() -> Dict[str, str]:
    with open(
        "sample_files/configured_catalog.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def config_aap() -> Dict[str, str]:
    with open(
        "sample_files/config-aap.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def config_aup() -> Dict[str, str]:
    with open(
        "sample_files/config-aup.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def invalid_config() -> Dict[str, str]:
    with open(
        "integration_tests/invalid_config.json",
    ) as f:
        yield load(f)


@fixture
def airbyte_state_message():
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            data={},
        ),
    )


@fixture
def airbyte_messages(airbyte_state_message):
    return [
        airbyte_state_message,
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="users",
                data={
                    "blocked": False,
                    "created_at": "2022-10-21T04:08:58.994Z",
                    "email": "beryl_becker95@yahoo.com",
                    "email_verified": False,
                    "family_name": "Blanda",
                    "given_name": "Bradly",
                    "identities": {
                        "user_id": "4ce74b28-bc00-4bbf-8a01-712dae975291",
                        "connection": "Username-Password-Authentication",
                        "provider": "auth0",
                        "isSocial": False,
                    },
                    "name": "Hope Rodriguez",
                    "nickname": "Terrence",
                    "updated_at": "2022-10-21T04:08:58.994Z",
                    "user_id": "auth0|4ce74b28-bc00-4bbf-8a01-712dae975291",
                },
                emitted_at=int(datetime.now().timestamp()) * 1000,
            ),
        ),
        airbyte_state_message,
    ]


def test_check_fails(invalid_config):
    destination = DestinationHeapAnalytics()
    status = destination.check(logger=MagicMock(), config=invalid_config)
    assert status.status == Status.FAILED


def test_check_succeeds(config_events, config_aap, config_aup):
    destination = DestinationHeapAnalytics()
    for config in [config_events, config_aap, config_aup]:
        status = destination.check(logger=MagicMock(), config=config)
        assert status.status == Status.SUCCEEDED


def test_write(
    config_events: Dict[str, Any],
    config_aap: Dict[str, Any],
    config_aup: Dict[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    airbyte_messages: List[AirbyteMessage],
    airbyte_state_message: AirbyteStateMessage,
):
    destination = DestinationHeapAnalytics()

    for config in [config_events, config_aap, config_aup]:
        generator = destination.write(config, configured_catalog, airbyte_messages)
        result = list(generator)
        assert len(result) == 3
        assert result[0] == airbyte_state_message
        assert result[1] == airbyte_state_message
        assert result[2].type == Type.LOG
        assert result[2].log.level == Level.INFO
        assert result[2].log.message == "Total Messages: 3. Total Records: 1. Total loaded: 1."
