#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import random
import string
from datetime import datetime
from json import dumps, load
from typing import Dict
from unittest.mock import MagicMock

from destination_firebolt.destination import DestinationFirebolt, establish_connection
from firebolt.common.exception import FireboltError
from pytest import fixture, mark, raises

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Status, Type
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)


@fixture(scope="module")
def config() -> Dict[str, str]:
    with open(
        "secrets/config.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def test_table_name() -> str:
    letters = string.ascii_lowercase
    rnd_string = "".join(random.choice(letters) for i in range(10))
    return f"airbyte_integration_{rnd_string}"


@fixture
def cleanup(config: Dict[str, str], test_table_name: str):
    yield
    with establish_connection(config, MagicMock()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS _airbyte_raw_{test_table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS ex_airbyte_raw_{test_table_name}")


@fixture
def table_schema() -> str:
    schema = {
        "type": "object",
        "properties": {
            "column1": {"type": ["null", "string"]},
        },
    }
    return schema


@fixture
def configured_catalogue(test_table_name: str, table_schema: str) -> ConfiguredAirbyteCatalog:
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name=test_table_name, json_schema=table_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


@fixture(scope="module")
def invalid_config() -> Dict[str, str]:
    with open(
        "integration_tests/invalid_config.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def invalid_config_s3() -> Dict[str, str]:
    with open(
        "integration_tests/invalid_config_s3.json",
    ) as f:
        yield load(f)


@fixture
def airbyte_message1(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name,
            data={"key1": "value1", "key2": 2},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@fixture
def airbyte_message2(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name,
            data={"key1": "value2", "key2": 3},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@mark.parametrize("config", ["invalid_config", "invalid_config_s3"])
def test_check_fails(config, request):
    destination = DestinationFirebolt()
    status = destination.check(logger=MagicMock(), config=config)
    assert status.status == Status.FAILED


def test_check_succeeds(config, request):
    destination = DestinationFirebolt()
    status = destination.check(logger=MagicMock(), config=config)
    assert status.status == Status.SUCCEEDED


def test_write(
    config: Dict[str, str],
    configured_catalogue: ConfiguredAirbyteCatalog,
    airbyte_message1: AirbyteMessage,
    airbyte_message2: AirbyteMessage,
    test_table_name: str,
    cleanup,
    request,
):
    destination = DestinationFirebolt()
    generator = destination.write(config, configured_catalogue, [airbyte_message1, airbyte_message2])
    result = list(generator)
    assert len(result) == 0
    with establish_connection(config, MagicMock()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT _airbyte_ab_id, _airbyte_emitted_at, _airbyte_data FROM _airbyte_raw_{test_table_name} ORDER BY _airbyte_data"
            )
            result = cursor.fetchall()
            # Make sure no temporary tables present
            with raises(FireboltError):
                cursor.execute(f"SELECT TOP 0 * FROM ex_airbyte_raw_{test_table_name}")
    assert len(result) == 2
    assert result[0][2] == dumps(airbyte_message1.record.data)
    assert result[1][2] == dumps(airbyte_message2.record.data)
