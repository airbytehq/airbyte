#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
import random
import string
import tempfile
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock

import duckdb
import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from destination_duckdb import DestinationDuckdb


@pytest.fixture(autouse=True)
def disable_destination_modification(monkeypatch, request):
    if "disable_autouse" in request.keywords:
        return
    else:
        monkeypatch.setattr(DestinationDuckdb, "_get_destination_path", lambda _, x: x)


@pytest.fixture(scope="module")
def local_file_config() -> Dict[str, str]:
    # create a file "myfile" in "mydir" in temp directory
    tmp_dir = tempfile.TemporaryDirectory()
    test = os.path.join(str(tmp_dir), "test.duckdb")

    # f1.write_text("text to myfile")
    yield {"destination_path": test}


@pytest.fixture(scope="module")
def test_table_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(10))
    return f"airbyte_integration_{rand_string}"


@pytest.fixture
def table_schema() -> str:
    schema = {"type": "object", "properties": {"column1": {"type": ["null", "string"]}}}
    return schema


@pytest.fixture
def configured_catalogue(test_table_name: str, table_schema: str) -> ConfiguredAirbyteCatalog:
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=test_table_name, json_schema=table_schema, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


@pytest.fixture
def invalid_config() -> Dict[str, str]:
    return {"destination_path": "/destination.duckdb"}


@pytest.fixture
def airbyte_message1(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name, data={"key1": "value1", "key2": 3}, emitted_at=int(datetime.now().timestamp()) * 1000
        ),
    )


@pytest.fixture
def airbyte_message2(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name, data={"key1": "value2", "key2": 2}, emitted_at=int(datetime.now().timestamp()) * 1000
        ),
    )


@pytest.fixture
def airbyte_message3():
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "1"}))


@pytest.mark.parametrize("config", ["invalid_config"])
@pytest.mark.disable_autouse
def test_check_fails(config, request):
    config = request.getfixturevalue(config)
    destination = DestinationDuckdb()
    status = destination.check(logger=MagicMock(), config=config)
    assert status.status == Status.FAILED


@pytest.mark.parametrize("config", ["local_file_config"])
def test_check_succeeds(config, request):
    config = request.getfixturevalue(config)
    destination = DestinationDuckdb()
    status = destination.check(logger=MagicMock(), config=config)
    assert status.status == Status.SUCCEEDED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


@pytest.mark.parametrize("config", ["local_file_config"])
def test_write(
    config: Dict[str, str],
    request,
    configured_catalogue: ConfiguredAirbyteCatalog,
    airbyte_message1: AirbyteMessage,
    airbyte_message2: AirbyteMessage,
    airbyte_message3: AirbyteMessage,
    test_table_name: str,
):
    config = request.getfixturevalue(config)
    destination = DestinationDuckdb()
    generator = destination.write(config, configured_catalogue, [airbyte_message1, airbyte_message2, airbyte_message3])

    result = list(generator)
    assert len(result) == 1

    con = duckdb.connect(database=config.get("destination_path"), read_only=False)
    with con:
        cursor = con.execute(
            f"SELECT _airbyte_ab_id, _airbyte_emitted_at, _airbyte_data FROM _airbyte_raw_{test_table_name} ORDER BY _airbyte_data"
        )
        result = cursor.fetchall()

    assert len(result) == 2
    assert result[0][2] == json.dumps(airbyte_message1.record.data)
    assert result[1][2] == json.dumps(airbyte_message2.record.data)
