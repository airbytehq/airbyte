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
    return logging.getLogger('airbyte')


def configured_catalog(test_table_name: str, table_schema: str) -> ConfiguredAirbyteCatalog:
    overwrite_stream = ConfiguredAirbyteStream(
        # TODO: I'm not sure if we should expect incoming streams SyncMode.incremental and only the destination to be full_refresh or they should
        stream=AirbyteStream(name=test_table_name, json_schema=table_schema,
                             supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])


def airbyte_message_record1(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name, data={"key_str": "value1", "key_int": 3}, emitted_at=int(datetime.now().timestamp()) * 1000
        ),
    )


def airbyte_message_record2(test_table_name: str):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=test_table_name, data={"key_str": "value2", "key_int": 2}, emitted_at=int(datetime.now().timestamp()) * 1000
        ),
    )


def airbyte_message_state(test_table_name: str):
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            data={"opaque": "to destination"}
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
    def test_write(self, mock_factory: Callable):
        mock_bigtable = CreateMockGlideBigTable()
        mock_factory.return_value = mock_bigtable

        destination = DestinationGlide()

        generator = destination.write(
            config=create_default_config(), configured_catalog=configured_catalog(self.test_table_name, table_schema=table_schema()), input_messages=[
                airbyte_message_record1(self.test_table_name), airbyte_message_record2(self.test_table_name), airbyte_message_state(self.test_table_name)]
        )

        # expecting only to return the state message:
        result = list(generator)
        assert len(result) == 1

        # todo: validate args on these calls
        mock_bigtable.prepare_table.assert_called_once()
        mock_bigtable.add_rows.assert_called_once()

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
            config=create_default_config(), configured_catalog=configured_catalog(self.test_table_name, table_schema=test_schema), input_messages=[
                airbyte_message_record1(self.test_table_name), airbyte_message_record2(self.test_table_name), airbyte_message_state(self.test_table_name)]
        )

        # expecting only to return the state message:
        result = list(generator)
        assert len(result) == 1

        mock_bigtable.prepare_table.assert_called_once()
        mock_bigtable.add_rows.assert_called_once()
        # get the columns we passed into teh API and verify the type defaulted to string:
        prepared_cols = mock_bigtable.prepare_table.call_args[0][0]
        null_column = [col for col in prepared_cols if col.id()
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
            config=config, configured_catalog=configured_catalog(self.test_table_name, table_schema=table_schema()), input_messages=[
                airbyte_message_record1(self.test_table_name), airbyte_message_record2(self.test_table_name), airbyte_message_state(self.test_table_name)]
        )
        # expecting only to return the state message:
        result = list(generator)

        passed_strategy = mock_factory.call_args[0][0]
        self.assertEqual("mutations", passed_strategy)
