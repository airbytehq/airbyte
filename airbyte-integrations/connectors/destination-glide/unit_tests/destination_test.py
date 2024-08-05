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
from destination_glide.glide import GlideBigTableBase, GlideBigTableFactory
from destination_glide.log import LOG_LEVEL_DEFAULT
import json
import logging
import random
import string
from typing import Any, Mapping, Callable
import unittest
from unittest.mock import patch, create_autospec, Mock


def create_default_config() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


def create_test_table_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(10))
    return f"test_table_{rand_string}"


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
    logger = logging.getLogger('airbyte')
    logger.setLevel(LOG_LEVEL_DEFAULT)


def create_configured_catalog_default(test_table_name: str, table_schema: str) -> ConfiguredAirbyteCatalog:
    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name=test_table_name, json_schema=table_schema,
                             supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])


def create_airbyte_message_record(stream_name: str, record_index: int):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream_name, data={"key_str": f"value{record_index}", "key_int": record_index}, emitted_at=int(datetime.now().timestamp()) * 1000
        ),
    )


def create_airbyte_message_state(stream_name: str):
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            data={"data is": " opaque to destination"}
        )
    )


def CreateMockGlideBigTable():
    return create_autospec(GlideBigTableBase)


class TestDestinationGlide(unittest.TestCase):
    api_host = 'https://test-api-host.com'
    api_key = 'test-api-key'
    api_path_root = '/test/api/path/root'
    table_id = 'test-table-id'

    def setUp(self):
        self.test_table_name = create_test_table_name()

    def test_check_with_valid_config(config: Mapping):
        outcome = DestinationGlide().check(AirbyteLogger(), config)
        assert outcome.status == Status.SUCCEEDED

    @patch.object(GlideBigTableFactory, "create")
    def test_write_simple(self, mock_factory: Callable):
        mock_bigtable = CreateMockGlideBigTable()
        mock_factory.return_value = mock_bigtable

        destination = DestinationGlide()

        generator = destination.write(
            config=create_default_config(),
            configured_catalog=create_configured_catalog_default(self.test_table_name,
                                                                 table_schema=table_schema()),
            input_messages=[
                create_airbyte_message_record(self.test_table_name, 1),
                create_airbyte_message_record(self.test_table_name, 2),
                create_airbyte_message_state(self.test_table_name)
            ]
        )

        # invoke the generator to get the results:
        result = list(generator)
        self.assertEqual(0, len(result))

        # ensure it called init, multiple add_rows, followed by commit:
        self.assertEqual(4, len(mock_bigtable.mock_calls))
        # NOTE: the call objects in Mock.mock_calls, are three-tuples of (name, positional args, keyword args).
        CALL_METHOD_NAME_INDEX = 0
        self.assertEqual(
            "init", mock_bigtable.mock_calls[0][CALL_METHOD_NAME_INDEX])
        self.assertEqual(
            "add_row", mock_bigtable.mock_calls[2][CALL_METHOD_NAME_INDEX])
        self.assertEqual(
            "commit", mock_bigtable.mock_calls[3][CALL_METHOD_NAME_INDEX])

    @patch.object(GlideBigTableFactory, "create")
    def test_write_with_checkpoints(self, mock_factory: Callable):
        """
        Ensures that the destination writes rows to the table as they are streamed from the source:
        """
        mock_bigtable = CreateMockGlideBigTable()
        mock_factory.return_value = mock_bigtable

        destination = DestinationGlide()

        # create enough records to cause a batch:
        RECORD_COUNT = 10
        input_messages = []
        input_messages.extend([create_airbyte_message_record(
            self.test_table_name, i) for i in range(RECORD_COUNT)])
        # create first checkpoint record:
        input_messages.append(create_airbyte_message_state(self.test_table_name))
        input_messages.extend([create_airbyte_message_record(
            self.test_table_name, i) for i in range(RECORD_COUNT)])
        # create second checkpoint record:
        input_messages.append(create_airbyte_message_state(self.test_table_name))

        generator = destination.write(
            config=create_default_config(),
            configured_catalog=create_configured_catalog_default(self.test_table_name,
                                                                 table_schema=table_schema()),
            input_messages=input_messages
        )

        # invoke the generator to get the results:
        result = list(generator)
        # we had two state records but we don't want to yield them
        self.assertEqual(0, len(result))

        # ensure it called add_rows multiple times:
        self.assertGreaterEqual(mock_bigtable.add_row.call_count, 2)
        # NOTE: the call objects in Mock.mock_calls, are three-tuples of (name, positional args, keyword args).
        CALL_METHOD_NAME_INDEX = 0
        self.assertEqual(
            "init", mock_bigtable.mock_calls[0][CALL_METHOD_NAME_INDEX])
        mock_bigtable.add_row.assert_called()
        self.assertEqual(
            "commit", mock_bigtable.mock_calls[mock_bigtable.call_count - 1][CALL_METHOD_NAME_INDEX])

    @patch.object(GlideBigTableFactory, "create", wraps=CreateMockGlideBigTable())
    def test_write_with_multiple_streams(self, mock_factory: Callable):
        """
        multiple streams should cause multiple tables to be created, and multiple stashes to be committed
        """
        # mock_bigtable = CreateMockGlideBigTable()
        # mock_factory.return_value = mock_bigtable

        destination = DestinationGlide()

        # create a catalog with multiple streams:
        streamA = ConfiguredAirbyteStream(
            stream=AirbyteStream(name="stream-a", json_schema=table_schema(),
                                 supported_sync_modes=[SyncMode.incremental]),
            sync_mode=SyncMode.incremental,
            destination_sync_mode=DestinationSyncMode.overwrite,
        )
        streamB = ConfiguredAirbyteStream(
            stream=AirbyteStream(name="stream-b", json_schema=table_schema(),
                                 supported_sync_modes=[SyncMode.incremental]),
            sync_mode=SyncMode.incremental,
            destination_sync_mode=DestinationSyncMode.overwrite,
        )

        configured_catalog = ConfiguredAirbyteCatalog(
            streams=[streamA, streamB])

        generator = destination.write(
            config=create_default_config(),
            configured_catalog=configured_catalog,
            input_messages=[
                create_airbyte_message_record("stream-a", 0),
                create_airbyte_message_record("stream-b", 0),
                create_airbyte_message_state("stream-a"),
                create_airbyte_message_state("stream-b")
            ]
        )

        # invoke the generator to get the results:
        result = list(generator)

        # multiple tables should have been created, and multiple stashes been committed
        self.assertEqual(mock_factory.call_count, 2)

    @patch.object(GlideBigTableFactory, "create")
    def test_with_invalid_column_types(self, mock_factory: Callable):
        mock_bigtable = CreateMockGlideBigTable()
        mock_factory.return_value = mock_bigtable

        destination = DestinationGlide()

        test_schema = {
            "type": "object",
            "properties": {
                "int_col": {"type": "integer"},
                # NOTE: null and object not supported by glide so this fails
                "obj_null_col": {"type": ["null", "object"]},
                "date_col": {"type": "string", "format": "date-time"},
            },
        }

        generator = destination.write(
            config=create_default_config(),
            configured_catalog=create_configured_catalog_default(self.test_table_name,
                                                                 table_schema=test_schema),
            input_messages=[
                create_airbyte_message_record(self.test_table_name, 1),
                create_airbyte_message_record(self.test_table_name, 2),
                create_airbyte_message_state(self.test_table_name)
            ]
        )

        # expecting not to return the state message:
        result = list(generator)
        assert len(result) == 0

        mock_bigtable.add_row.assert_called()
        # get the columns we passed into teh API and verify the type defaulted to string:
        schema_calls = mock_bigtable.init.call_args[0][2]
        null_column = [col for col in schema_calls if col.id()
                       == "obj_null_col"][0]
        self.assertEqual(null_column.type(), "string")
