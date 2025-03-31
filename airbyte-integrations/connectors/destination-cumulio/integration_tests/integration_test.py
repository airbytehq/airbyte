#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import time
from logging import Logger, getLogger
from typing import Any, Dict, Mapping

import pytest
from destination_cumulio import DestinationCumulio
from destination_cumulio.client import CumulioClient

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


@pytest.fixture(name="logger")
def logger_fixture() -> Logger:
    return getLogger("airbyte")


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {
            "string_col": {"type": "str"},
            "int_col": {"type": "integer"},
            "obj_col": {"type": "object"},
            "arr_col": {"type": "array"},
        },
    }

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="append_integration_test_stream",
            json_schema=stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="overwrite_integration_test_stream",
            json_schema=stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream])


@pytest.fixture(autouse=True)
def delete_datasets(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, logger: Logger):
    cumulio_client = CumulioClient(config, logger)
    for stream in configured_catalog.streams:
        dataset = cumulio_client.get_dataset_and_columns_from_stream_name(stream.stream.name)
        if dataset:
            logger.info(
                f"Existing integration test dataset found. Will delete Cumul.io dataset for integration test stream {stream.stream.name}."
            )
            try:
                cumulio_client.client.delete("securable", dataset["id"])
            except Exception as e:
                logger.info(
                    f"The following exception occurred when trying to delete the dataset "
                    f"for integration test stream {stream.stream.name}: {e}"
                )


def test_check_valid_config(config: Mapping, logger: Logger):
    outcome = DestinationCumulio().check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_check_incomplete_config(logger: Logger):
    outcome = DestinationCumulio().check(logger, {"api_host": "https://api.cumul.io"})
    assert outcome.status == Status.FAILED


def test_check_invalid_config(logger: Logger):
    outcome = DestinationCumulio().check(
        logger,
        {
            "api_host": ".invalid.url",
            "api_key": "invalid_key",
            "api_token": "invalid_token",
        },
    )
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream_name: str, str_value: str, int_value: int, obj_value: dict, arr_value: list) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream_name,
            data={
                "string_col": str_value,
                "int_col": int_value,
                "obj_col": obj_value,
                "arr_col": arr_value,
            },
            emitted_at=0,
        ),
    )


def _retrieve_all_records(cumulio_client, stream_name):
    dataset_and_columns = cumulio_client.get_dataset_and_columns_from_stream_name(stream_name)
    # Wait 5 seconds before trying to retrieve the data to ensure it can be properly retrieved
    time.sleep(5)
    if dataset_and_columns is not None:
        ordered_columns = cumulio_client.get_ordered_columns(stream_name)
        dimension_columns = list(
            map(
                lambda x, y: {
                    "dataset_id": dataset_and_columns["id"],
                    "column_id": y["id"],
                },
                ordered_columns,
                dataset_and_columns["columns"],
            )
        )
        int_col_ind = ordered_columns.index("int_col")

        raw_data_query = {
            "dimensions": dimension_columns,
            "options": {"rollup_data": False},
            "order": [
                {
                    "dataset_id": dataset_and_columns["id"],
                    "column_id": dataset_and_columns["columns"][int_col_ind]["id"],
                    "order": "asc",
                }
            ],
        }
        raw_data = cumulio_client.client.get("data", raw_data_query)
        airbyte_data_to_return = []
        for row in raw_data["data"]:
            airbyte_data_row = {}
            for col_ind, column in enumerate(dataset_and_columns["columns"]):
                if isinstance(row[col_ind], dict):
                    airbyte_data_row[column["source_name"]] = row[col_ind]["id"]
                else:
                    airbyte_data_row[column["source_name"]] = row[col_ind]
            airbyte_data_to_return.append(
                AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=airbyte_data_row, emitted_at=0),
                )
            )
        return airbyte_data_to_return
    return None


def test_write_append(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    logger: Logger,
):
    """
    This test verifies that:
     - Writing a stream in "append" mode appends new records while preserving existing data.
     - The correct state message is output by the connector at the end of the sync.
     - Object and Array data is appropriately stringified in Cumul.io.
    """
    stream_name = configured_catalog.streams[0].stream.name
    destination = DestinationCumulio()

    state_message = _state({"state": "3"})
    record_chunk_1 = [_record(stream_name, "test-" + str(i), i, {"test": i}, ["test", i]) for i in range(1, 3)]

    output_states_1 = list(destination.write(config, configured_catalog, [*record_chunk_1, state_message]))
    assert [state_message] == output_states_1

    record_chunk_2 = [_record(stream_name, "test-" + str(i), i, {"test": i}, ["test", i]) for i in range(3, 5)]

    output_states_2 = list(destination.write(config, configured_catalog, [*record_chunk_2, state_message]))
    assert [state_message] == output_states_2

    cumulio_client = CumulioClient(config, logger)

    records_in_destination = _retrieve_all_records(cumulio_client, stream_name)

    expected_records = [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=stream_name,
                data={
                    "string_col": "test-" + str(i),
                    "int_col": i,
                    "obj_col": json.dumps({"test": i}),
                    "arr_col": json.dumps(["test", i]),
                },
                emitted_at=0,
            ),
        )
        for i in range(1, 5)
    ]

    assert expected_records == records_in_destination


def test_write_overwrite(
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    logger: Logger,
):
    """
    This test verifies that:
     - writing a stream in "append" mode overwrite all exiting data.
     - the correct state message is output by the connector at the end of the sync.
     - Object and Array data is appropriately stringified in Cumul.io.
    """
    stream_name = configured_catalog.streams[1].stream.name
    destination = DestinationCumulio()

    state_message = _state({"state": "3"})
    record_chunk_1 = [_record(stream_name, "oldtest-" + str(i), i, {"oldtest": i}, ["oldtest", i]) for i in range(1, 3)]

    output_states_1 = list(destination.write(config, configured_catalog, [*record_chunk_1, state_message]))
    assert [state_message] == output_states_1

    record_chunk_2 = [_record(stream_name, "newtest-" + str(i), i, {"newtest": i}, ["newtest", i]) for i in range(1, 3)]

    output_states_2 = list(destination.write(config, configured_catalog, [*record_chunk_2, state_message]))
    assert [state_message] == output_states_2

    cumulio_client = CumulioClient(config, logger)

    records_in_destination = _retrieve_all_records(cumulio_client, stream_name)

    expected_records = [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=stream_name,
                data={
                    "string_col": "newtest-" + str(i),
                    "int_col": i,
                    "obj_col": json.dumps({"newtest": i}),
                    "arr_col": json.dumps(["newtest", i]),
                },
                emitted_at=0,
            ),
        )
        for i in range(1, 3)
    ]

    assert expected_records == records_in_destination
