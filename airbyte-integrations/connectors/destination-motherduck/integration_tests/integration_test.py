# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
import os
import random
import string
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable
from unittest.mock import MagicMock

import duckdb
import pytest
from destination_motherduck import DestinationMotherDuck
from destination_motherduck.destination import CONFIG_MOTHERDUCK_API_KEY
from faker import Faker

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
from airbyte_cdk.sql.secrets import SecretString


CONFIG_PATH = "integration_tests/config.json"
SECRETS_CONFIG_PATH = "secrets/config.json"  # Should contain a valid MotherDuck API token


def pytest_generate_tests(metafunc):
    if "config" not in metafunc.fixturenames:
        return

    configs: list[str] = ["local_file_config"]
    if Path(SECRETS_CONFIG_PATH).is_file():
        configs.append("motherduck_config")
    else:
        print(f"Skipping MotherDuck tests because config file not found at: {SECRETS_CONFIG_PATH}")

    # for test_name in ["test_check_succeeds", "test_write"]:
    metafunc.parametrize("config", configs, indirect=True)


@pytest.fixture(scope="module")
def test_schema_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(6))
    return f"test_schema_{rand_string}"


@pytest.fixture
def config(request, test_schema_name: str) -> Generator[Any, Any, Any]:
    if request.param == "local_file_config":
        tmp_dir = tempfile.TemporaryDirectory()
        test = os.path.join(str(tmp_dir.name), "test.duckdb")
        yield {"destination_path": test, "schema": test_schema_name}

    elif request.param == "motherduck_config":
        config_dict = json.loads(Path(SECRETS_CONFIG_PATH).read_text())
        config_dict["schema"] = test_schema_name
        if CONFIG_MOTHERDUCK_API_KEY in config_dict:
            # Prevent accidentally printing API Key if `config_dict` is printed.
            config_dict[CONFIG_MOTHERDUCK_API_KEY] = SecretString(config_dict[CONFIG_MOTHERDUCK_API_KEY])
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
        monkeypatch.setattr(DestinationMotherDuck, "_get_destination_path", lambda _, x: x)


@pytest.fixture(scope="module")
def test_table_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(10))
    return f"airbyte_integration_{rand_string}"


@pytest.fixture(scope="module")
def other_test_table_name(test_table_name) -> str:
    return test_table_name + "_other"


@pytest.fixture
def test_large_table_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(10))
    return f"airbyte_integration_{rand_string}"


@pytest.fixture
def table_schema() -> str:
    schema = {
        "type": "object",
        "properties": {
            "key1": {"type": ["null", "string"]},
            "key2": {"type": ["null", "string"]},
        },
    }
    return schema


@pytest.fixture
def other_table_schema() -> str:
    schema = {
        "type": "object",
        "properties": {
            "key3": {"type": ["null", "string"]},
            "default": {"type": ["null", "string"]},
        },
    }
    return schema


@pytest.fixture
def configured_catalogue(
    test_table_name: str,
    other_test_table_name: str,
    test_large_table_name: str,
    table_schema: str,
    other_table_schema: str,
) -> ConfiguredAirbyteCatalog:
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=test_table_name,
            json_schema=table_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
        primary_key=[["key1"]],
    )
    other_append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=other_test_table_name,
            json_schema=other_table_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
        primary_key=[["key3"]],
    )
    append_stream_large = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=test_large_table_name,
            json_schema=table_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
        primary_key=[["key1"]],
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream, other_append_stream, append_stream_large])


@pytest.fixture
def configured_catalogue_append_dedup(
    test_table_name: str,
    test_large_table_name: str,
    table_schema: str,
) -> ConfiguredAirbyteCatalog:
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=test_table_name,
            json_schema=table_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
        primary_key=[["key1"]],
    )
    append_stream_large = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=test_large_table_name,
            json_schema=table_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
        primary_key=[["key1"]],
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream, append_stream_large])


@pytest.fixture
def airbyte_message1(test_table_name: str):
    fake = Faker()
    Faker.seed(0)
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name,
            data={"key1": fake.unique.first_name(), "key2": str(fake.ssn())},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.fixture
def airbyte_message2(test_table_name: str):
    fake = Faker()
    Faker.seed(1)
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name,
            data={"key1": fake.unique.first_name(), "key2": str(fake.ssn())},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.fixture
def airbyte_message2_update(airbyte_message2: AirbyteMessage, test_table_name: str):
    fake = Faker()
    Faker.seed(1)
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name,
            data={
                "key1": airbyte_message2.record.data["key1"],
                "key2": str(fake.ssn()),
            },
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.fixture
def airbyte_message3():
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "1"}))


@pytest.fixture
def airbyte_message4(other_test_table_name: str):
    fake = Faker()
    Faker.seed(0)
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=other_test_table_name,
            data={"key3": fake.unique.first_name(), "default": str(fake.ssn())},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.fixture
def airbyte_message5(other_test_table_name: str):
    fake = Faker()
    Faker.seed(1)
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=other_test_table_name,
            data={"key3": fake.unique.first_name(), "default": str(fake.ssn())},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@pytest.mark.disable_autouse
def test_check_fails(invalid_config, request):
    destination = DestinationMotherDuck()
    status = destination.check(logger=MagicMock(), config=invalid_config)
    assert status.status == Status.FAILED


def test_check_succeeds(
    config: dict[str, str],
    request,
):
    destination = DestinationMotherDuck()
    status = destination.check(logger=MagicMock(), config=config)
    assert status.status == Status.SUCCEEDED, status.message


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


@pytest.fixture()
def sql_processor(configured_catalogue, test_schema_name, config: Dict[str, str]):
    destination = DestinationMotherDuck()
    path = config.get("destination_path", "md:")
    if CONFIG_MOTHERDUCK_API_KEY in config:
        processor = destination._get_sql_processor(
            configured_catalog=configured_catalogue,
            schema_name=test_schema_name,
            db_path=path,
            motherduck_token=config[CONFIG_MOTHERDUCK_API_KEY],
        )
    else:
        processor = destination._get_sql_processor(
            configured_catalog=configured_catalogue,
            schema_name=test_schema_name,
            db_path=path,
        )
    return processor


def test_write(
    config: Dict[str, str],
    request,
    configured_catalogue: ConfiguredAirbyteCatalog,
    airbyte_message1: AirbyteMessage,
    airbyte_message2: AirbyteMessage,
    airbyte_message3: AirbyteMessage,
    airbyte_message4: AirbyteMessage,
    airbyte_message5: AirbyteMessage,
    test_table_name: str,
    test_schema_name: str,
    test_large_table_name: str,
    sql_processor,
):
    destination = DestinationMotherDuck()
    generator = destination.write(
        config,
        configured_catalogue,
        [airbyte_message1, airbyte_message2, airbyte_message3, airbyte_message4, airbyte_message5],
    )

    result = list(generator)
    assert len(result) == 1

    sql_result = sql_processor._execute_sql(
        "SELECT key1, key2, _airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta "
        f"FROM {test_schema_name}.{test_table_name} ORDER BY key1"
    )

    assert len(sql_result) == 2
    assert sql_result[0][0] == "Dennis"
    assert sql_result[1][0] == "Megan"
    assert sql_result[0][1] == "868-98-1034"
    assert sql_result[1][1] == "777-54-0664"


def test_write_dupe(
    config: Dict[str, str],
    request,
    configured_catalogue_append_dedup: ConfiguredAirbyteCatalog,
    airbyte_message1: AirbyteMessage,
    airbyte_message2: AirbyteMessage,
    airbyte_message2_update: AirbyteMessage,
    airbyte_message3: AirbyteMessage,
    test_table_name: str,
    test_schema_name: str,
    sql_processor,
):
    destination = DestinationMotherDuck()
    generator = destination.write(
        config,
        configured_catalogue_append_dedup,
        [airbyte_message1, airbyte_message2, airbyte_message2_update, airbyte_message3],
    )

    result = list(generator)
    assert len(result) == 1

    sql_result = sql_processor._execute_sql(
        "SELECT key1, key2, _airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta "
        f"FROM {test_schema_name}.{test_table_name} ORDER BY key1"
    )

    assert len(sql_result) == 2
    assert sql_result[0][0] == "Dennis"
    assert sql_result[1][0] == "Megan"
    assert sql_result[0][1] == "138-73-1034"
    assert sql_result[1][1] == "777-54-0664"


def _airbyte_messages(n: int, batch_size: int, table_name: str) -> Generator[AirbyteMessage, None, None]:
    fake = Faker()
    Faker.seed(0)

    for i in range(n):
        if i != 0 and i % batch_size == 0:
            yield AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(data={"state": str(i // batch_size)}),
            )
        else:
            message = AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream=table_name,
                    data={"key1": fake.unique.name(), "key2": str(fake.ssn())},
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
                type=Type.STATE,
                state=AirbyteStateMessage(data={"state": str(i // batch_size)}),
            )
        else:
            message = AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream=table_name,
                    # Throw in empty nested objects and see how pyarrow deals with them.
                    data=(
                        {
                            "key1": fake.unique.name(),
                            "key2": str(fake.ssn()) if random.random() < 0.5 else str(random.randrange(1000, 9999999999999)),
                            "nested1": (
                                {}
                                if random.random() < 0.1
                                else {
                                    "key3": fake.first_name(),
                                    "key4": str(fake.ssn()) if random.random() < 0.5 else random.randrange(1000, 9999999999999),
                                    "dictionary1": (
                                        {}
                                        if random.random() < 0.1
                                        else {
                                            "key3": fake.first_name(),
                                            "key4": "True" if random.random() < 0.5 else True,
                                        }
                                    ),
                                }
                            ),
                        }
                        if random.random() < 0.9
                        else {
                            "key1": fake.unique.name(),
                        }
                    ),
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
            yield message


TOTAL_RECORDS = 5_000
BATCH_WRITE_SIZE = 1000


@pytest.mark.slow
@pytest.mark.parametrize(
    "airbyte_message_generator,explanation",
    [
        (_airbyte_messages, "Test writing a large number of simple json objects."),
        (
            _airbyte_messages_with_inconsistent_json_fields,
            "Test writing a large number of json messages with inconsistent schema.",
        ),
    ],
)
def test_large_number_of_writes(
    config: Dict[str, str],
    request,
    configured_catalogue: ConfiguredAirbyteCatalog,
    test_large_table_name: str,
    test_schema_name: str,
    airbyte_message_generator: Callable[[int, int, str], Iterable[AirbyteMessage]],
    explanation: str,
    sql_processor,
):
    destination = DestinationMotherDuck()
    generator = destination.write(
        config,
        configured_catalogue,
        airbyte_message_generator(TOTAL_RECORDS, BATCH_WRITE_SIZE, test_large_table_name),
    )

    result = list(generator)
    assert len(result) == TOTAL_RECORDS // (BATCH_WRITE_SIZE + 1)

    sql_result = sql_processor._execute_sql("SELECT count(1) " f"FROM {test_schema_name}.{test_large_table_name}")
    assert sql_result[0][0] == TOTAL_RECORDS - TOTAL_RECORDS // (BATCH_WRITE_SIZE + 1)
