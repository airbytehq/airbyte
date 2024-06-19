#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
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
    Type
)
from datetime import datetime
from destination_glide import DestinationGlide
# for mock:
from destination_glide.glide import GlideBigTableBase

import json
import logging
import pytest
import random
import string
from typing import Any, Mapping
from unittest.mock import create_autospec

@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(scope="module")
def test_table_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(10))
    return f"airbyte_integration_{rand_string}"


@pytest.fixture
def table_schema() -> str:
    stream_schema = {
        "type": "object",
        "properties": {
            "string_col": {"type": "string"},
            "int_col": {"type": "integer"},
            "date_col": {"type": "string", "format": "date-time"},
            "other_col": {"type": ["null", "string"]}
        },
    }
    return stream_schema


def AirbyteLogger() -> logging.Logger:
    return logging.getLogger('airbyte')

@pytest.fixture
def configured_catalog(test_table_name: str, table_schema: str) -> ConfiguredAirbyteCatalog:
    overwrite_stream = ConfiguredAirbyteStream(
        # TODO: I'm not sure if we should expect incoming streams SyncMode.incremental and only the destination to be full_refresh or they should
        stream=AirbyteStream(name=test_table_name, json_schema=table_schema,
                             supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])

@pytest.fixture
def airbyte_message_record1(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name, data={"key_str": "value1", "key_int": 3}, emitted_at=int(datetime.now().timestamp()) * 1000
        ),
    )

@pytest.fixture
def airbyte_message_record2(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name, data={"key_str": "value2", "key_int": 2}, emitted_at=int(datetime.now().timestamp()) * 1000
        ),
    )


@pytest.fixture
def airbyte_message_state(test_table_name: str):
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            data={"opaque": "to destination"}
        )
    )


#configured_stream.stream.json_schema["properties"]

##### Tests Begin Here #####


def test_check_valid_config(config: Mapping):
    outcome = DestinationGlide().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED


def test_write(
    config: Mapping,
    request,
    configured_catalog: ConfiguredAirbyteCatalog,
    airbyte_message_record1: AirbyteMessage,
    airbyte_message_record2: AirbyteMessage,
    airbyte_message_state: AirbyteMessage,
    test_table_name: str,
):
    mock_gbt = create_autospec(GlideBigTableBase)

    destination = DestinationGlide(mock_gbt)
    generator = destination.write(
        config=config, configured_catalog=configured_catalog, input_messages=[
            airbyte_message_record1, airbyte_message_record1, airbyte_message_state]
    )

    # expecting only to return the state message:
    result = list(generator)
    assert len(result) == 1

    # expect the API was called:
    # todo: validate args on these calls
    
    mock_gbt.delete_all.assert_called_once()
    mock_gbt.add_rows.assert_called_once()
