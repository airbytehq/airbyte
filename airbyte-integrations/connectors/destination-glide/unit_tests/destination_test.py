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


def configured_catalog(test_table_name: str, table_schema: str) -> ConfiguredAirbyteCatalog:
    overwrite_stream = ConfiguredAirbyteStream(
        # TODO: I'm not sure if we should expect incoming streams SyncMode.incremental and only the destination to be full_refresh or they should
        stream=AirbyteStream(name=test_table_name, json_schema=table_schema,
                             supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])


def create_airbyte_message_record(test_table_name: str, record_index: int):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name, data={"key_str": f"value{record_index}", "key_int": record_index}, emitted_at=int(datetime.now().timestamp()) * 1000
        ),
    )


def airbyte_message_state(test_table_name: str):
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
            configured_catalog=configured_catalog(self.test_table_name,
                                                  table_schema=table_schema()),
            input_messages=[
                create_airbyte_message_record(self.test_table_name, 1),
                create_airbyte_message_record(self.test_table_name, 2),
                airbyte_message_state(self.test_table_name)
            ]
        )

        # invoke the generator to get the results:
        result = list(generator)
        self.assertEqual(1, len(result))

        # ensure it called set_schema, multiple add_rows, followed by commit:
        self.assertEqual(4, len(mock_bigtable.mock_calls))
        # NOTE: the call objects in Mock.mock_calls, are three-tuples of (name, positional args, keyword args).
        CALL_METHOD_NAME_INDEX = 0
        self.assertEqual(
            "init", mock_bigtable.mock_calls[0][CALL_METHOD_NAME_INDEX])
        self.assertEqual(
            "set_schema", mock_bigtable.mock_calls[1][CALL_METHOD_NAME_INDEX])
        self.assertEqual(
            "add_rows", mock_bigtable.mock_calls[2][CALL_METHOD_NAME_INDEX])
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
        input_messages.append(airbyte_message_state(self.test_table_name))
        input_messages.extend([create_airbyte_message_record(
            self.test_table_name, i) for i in range(RECORD_COUNT)])
        # create second checkpoint record:
        input_messages.append(airbyte_message_state(self.test_table_name))

        generator = destination.write(
            config=create_default_config(),
            configured_catalog=configured_catalog(self.test_table_name,
                                                  table_schema=table_schema()),
            input_messages=input_messages
        )

        # invoke the generator to get the results:
        result = list(generator)
        # we had two state records so we expect them to be yielded:
        self.assertEqual(2, len(result))

        # ensure it called add_rows multiple times:
        self.assertGreaterEqual(mock_bigtable.add_rows.call_count, 2)
        # NOTE: the call objects in Mock.mock_calls, are three-tuples of (name, positional args, keyword args).
        CALL_METHOD_NAME_INDEX = 0
        self.assertEqual(
            "init", mock_bigtable.mock_calls[0][CALL_METHOD_NAME_INDEX])
        self.assertEqual(
            "set_schema", mock_bigtable.mock_calls[1][CALL_METHOD_NAME_INDEX])
        mock_bigtable.add_rows.assert_called()
        self.assertEqual(
            "commit", mock_bigtable.mock_calls[mock_bigtable.call_count - 1][CALL_METHOD_NAME_INDEX])

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
            configured_catalog=configured_catalog(self.test_table_name,
                                                  table_schema=test_schema),
            input_messages=[
                create_airbyte_message_record(self.test_table_name, 1),
                create_airbyte_message_record(self.test_table_name, 2),
                airbyte_message_state(self.test_table_name)
            ]
        )

        # expecting only to return the state message:
        result = list(generator)
        assert len(result) == 1

        mock_bigtable.set_schema.assert_called_once()
        mock_bigtable.add_rows.assert_called_once()
        # get the columns we passed into teh API and verify the type defaulted to string:
        schema_calls = mock_bigtable.set_schema.call_args[0][0]
        null_column = [col for col in schema_calls if col.id()
                       == "obj_null_col"][0]
        self.assertEqual(null_column.type(), "string")

    @patch.object(GlideBigTableFactory, "create")
    def test_api_version_passes_correct_strategy(self, mock_factory: Mock):
        mock_bigtable = CreateMockGlideBigTable()
        mock_factory.return_value = mock_bigtable

        config = {
            "api_host": "foo",
            "api_path_root": "bar",
            "api_key": "baz",
            "table_id": "buz",
            "glide_api_version": "mutations"
        }

        destination = DestinationGlide()
        generator = destination.write(
            config=config,
            configured_catalog=configured_catalog(
                self.test_table_name, table_schema=table_schema()),
            input_messages=[
                create_airbyte_message_record(self.test_table_name, 1),
                create_airbyte_message_record(self.test_table_name, 2),
                airbyte_message_state(self.test_table_name)
            ]
        )
        # expecting only to return the state message:
        result = list(generator)

        passed_strategy = mock_factory.call_args[0][0]
        self.assertEqual("mutations", passed_strategy)
