#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import json
import os
import random
import string
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable
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
from destination_duckdb.destination import CONFIG_MOTHERDUCK_API_KEY
from faker import Faker

CONFIG_PATH = "integration_tests/config.json"
SECRETS_CONFIG_PATH = (
    "secrets/config.json"  # Should contain a valid MotherDuck API token
)


def pytest_generate_tests(metafunc):
    if "config" not in metafunc.fixturenames:
        return

    configs: list[str] = ["local_file_config"]
    if Path(SECRETS_CONFIG_PATH).is_file():
        configs.append("motherduck_config")
    else:
        print(
            f"Skipping MotherDuck tests because config file not found at: {SECRETS_CONFIG_PATH}"
        )

    # for test_name in ["test_check_succeeds", "test_write"]:
    metafunc.parametrize("config", configs, indirect=True)


@pytest.fixture(scope="module")
def test_schema_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(6))
    return f"test_schema_{rand_string}"


@pytest.fixture
def config(request, test_schema_name: str) -> Dict[str, str]:
    if request.param == "local_file_config":
        tmp_dir = tempfile.TemporaryDirectory()
        test = os.path.join(str(tmp_dir.name), "test.duckdb")
        yield {"destination_path": test, "schema": test_schema_name}

    elif request.param == "motherduck_config":
        config_dict = json.loads(Path(SECRETS_CONFIG_PATH).read_text())
        config_dict["schema"] = test_schema_name
        yield config_dict

    else:
        raise ValueError(f"Unknown config type: {request.param}")


@pytest.fixture
def invalid_config() -> Dict[str, str]:
    return {"destination_path": "/destination.duckdb"}


@pytest.fixture(autouse=True)
def disable_destination_modification(monkeypatch, request):
    if "disable_autouse" in request.keywords:
        return
    else:
        monkeypatch.setattr(DestinationDuckdb, "_get_destination_path", lambda _, x: x)


@pytest.fixture(scope="module")
def test_table_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(10))
    return f"airbyte_integration_{rand_string}"


@pytest.fixture
def test_large_table_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(10))
    return f"airbyte_integration_{rand_string}"

@pytest.fixture
def table_schema() -> str:
    schema = {"type": "object", "properties": {"column1": {"type": ["null", "string"]}}}
    return schema


@pytest.fixture
def configured_catalogue(
    test_table_name: str, test_large_table_name: str, table_schema: str, 
) -> ConfiguredAirbyteCatalog:
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=test_table_name,
            json_schema=table_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    append_stream_large = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=test_large_table_name,
            json_schema=table_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream, append_stream_large])


@pytest.fixture
def airbyte_message1(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name,
            data={"key1": "value1", "key2": 3},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.fixture
def airbyte_message2(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name,
            data={"key1": "value2", "key2": 2},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.fixture
def airbyte_message3():
    return AirbyteMessage(
        type=Type.STATE, state=AirbyteStateMessage(data={"state": "1"})
    )


@pytest.mark.disable_autouse
def test_check_fails(invalid_config, request):
    destination = DestinationDuckdb()
    status = destination.check(logger=MagicMock(), config=invalid_config)
    assert status.status == Status.FAILED


def test_check_succeeds(
    config: dict[str, str],
    request,
):
    destination = DestinationDuckdb()
    status = destination.check(logger=MagicMock(), config=config)
    assert status.status == Status.SUCCEEDED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def test_write(
    config: Dict[str, str],
    request,
    configured_catalogue: ConfiguredAirbyteCatalog,
    airbyte_message1: AirbyteMessage,
    airbyte_message2: AirbyteMessage,
    airbyte_message3: AirbyteMessage,
    test_table_name: str,
    test_schema_name: str,
):
    destination = DestinationDuckdb()
    generator = destination.write(
        config,
        configured_catalogue,
        [airbyte_message1, airbyte_message2, airbyte_message3],
    )

    result = list(generator)
    assert len(result) == 1
    motherduck_api_key = str(config.get(CONFIG_MOTHERDUCK_API_KEY, ""))
    duckdb_config = {}
    if motherduck_api_key:
        duckdb_config["motherduck_token"] = motherduck_api_key
        duckdb_config["custom_user_agent"] = "airbyte_intg_test"
    con = duckdb.connect(
        database=config.get("destination_path"), read_only=False, config=duckdb_config
    )
    with con:
        cursor = con.execute(
            "SELECT _airbyte_ab_id, _airbyte_emitted_at, _airbyte_data "
            f"FROM {test_schema_name}._airbyte_raw_{test_table_name} ORDER BY _airbyte_data"
        )
        result = cursor.fetchall()

    assert len(result) == 2
    assert result[0][2] == json.dumps(airbyte_message1.record.data)
    assert result[1][2] == json.dumps(airbyte_message2.record.data)

def _airbyte_messages(n: int, batch_size: int, table_name: str) -> Generator[AirbyteMessage, None, None]:
    fake = Faker()
    Faker.seed(0)

    for i in range(n):
        if i != 0 and i % batch_size == 0:
            yield AirbyteMessage(
                type=Type.STATE, state=AirbyteStateMessage(data={"state": str(i // batch_size)})
            )
        else:
            message = AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream=table_name,
                    data={"key1": fake.first_name() , "key2": fake.ssn()},
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
            yield message


def _airbyte_messages_with_inconsistent_json_fields(n: int, batch_size: int, table_name: str) -> Generator[AirbyteMessage, None, None]:
    fake = Faker()
    Faker.seed(0)
    random.seed(0)

    for i in range(n):
        if i != 0 and i % batch_size == 0:
            yield AirbyteMessage(
                type=Type.STATE, state=AirbyteStateMessage(data={"state": str(i // batch_size)})
            )
        else:
            message = AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream=table_name,
                    # Throw in empty nested objects and see how pyarrow deals with them.
                    data={"key1": fake.first_name() , 
                          "key2": fake.ssn() if random.random()< 0.5 else random.randrange(1000,9999999999999), 
                          "nested1": {} if random.random()< 0.1 else { 
                              "key3": fake.first_name() , 
                              "key4": fake.ssn() if random.random()< 0.5 else random.randrange(1000,9999999999999), 
                              "dictionary1":{} if random.random()< 0.1 else { 
                                  "key3": fake.first_name() , 
                                  "key4": "True" if random.random() < 0.5 else True
                                  }
                              }
                          } 
                          if random.random() < 0.9 else {},

                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
            yield message


TOTAL_RECORDS = 5_000
BATCH_WRITE_SIZE = 1000

@pytest.mark.slow
@pytest.mark.parametrize("airbyte_message_generator,explanation", 
                         [(_airbyte_messages, "Test writing a large number of simple json objects."), 
                          (_airbyte_messages_with_inconsistent_json_fields, "Test writing a large number of json messages with inconsistent schema.")] )
def test_large_number_of_writes(
    config: Dict[str, str],
    request,
    configured_catalogue: ConfiguredAirbyteCatalog,
    test_large_table_name: str,
    test_schema_name: str,
    airbyte_message_generator: Callable[[int, int, str], Iterable[AirbyteMessage]],
    explanation: str,
):
    destination = DestinationDuckdb()
    generator = destination.write(
        config,
        configured_catalogue,
        airbyte_message_generator(TOTAL_RECORDS, BATCH_WRITE_SIZE, test_large_table_name),
    )

    result = list(generator)
    assert len(result) == TOTAL_RECORDS // (BATCH_WRITE_SIZE + 1)
    motherduck_api_key = str(config.get(CONFIG_MOTHERDUCK_API_KEY, ""))
    duckdb_config = {}
    if motherduck_api_key:
        duckdb_config["motherduck_token"] = motherduck_api_key
        duckdb_config["custom_user_agent"] = "airbyte_intg_test"

    con = duckdb.connect(
        database=config.get("destination_path"), read_only=False, config=duckdb_config
    )
    with con:
        cursor = con.execute(
            "SELECT count(1) "
            f"FROM {test_schema_name}._airbyte_raw_{test_large_table_name}"
        )
        result = cursor.fetchall()
    assert result[0][0] == TOTAL_RECORDS - TOTAL_RECORDS // (BATCH_WRITE_SIZE + 1)
