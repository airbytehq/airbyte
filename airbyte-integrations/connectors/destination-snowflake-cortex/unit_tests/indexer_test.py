#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, cast
from unittest.mock import ANY, MagicMock, Mock, call, patch

from airbyte.strategies import WriteStrategy
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, AirbyteStateMessage, AirbyteStreamState, ConfiguredAirbyteCatalog, Type
from destination_snowflake_cortex.config import SnowflakeCortexIndexingModel
from destination_snowflake_cortex.indexer import (
    CHUNK_ID_COLUMN,
    DOCUMENT_CONTENT_COLUMN,
    DOCUMENT_ID_COLUMN,
    EMBEDDING_COLUMN,
    METADATA_COLUMN,
    SnowflakeCortexIndexer,
)


def _create_snowflake_cortex_indexer(catalog:Optional[ConfiguredAirbyteCatalog] ):
    snowflake_credentials = {
        "host": "account",
        "role": "role",
        "warehouse": "warehouse",
        "database": "database",
        "default_schema": "schema",
        "username": "username",
        "credentials": {
            "password": "xxxxxx"
        }
    }
    config = SnowflakeCortexIndexingModel(**snowflake_credentials)
    with patch.object(SnowflakeCortexIndexer, '_init_db_connection', side_effect=None):
        indexer = SnowflakeCortexIndexer(config, 3, Mock(ConfiguredAirbyteCatalog) if catalog is None else catalog)
    return indexer 

def test_get_airbyte_messsages_from_chunks():
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    messages = indexer._get_airbyte_messsages_from_chunks(
        [
            Mock(page_content="test1", 
                 metadata={"_ab_stream": "abc"}, 
                 embedding=[1, 2, 3], 
                 record=AirbyteRecordMessage(namespace=None, stream='example_stream', data={'str_col': 'Dogs are number 0', 'int_col': 4}, emitted_at=0)),
            Mock(page_content="test2", 
                 metadata={"_ab_stream": "abc"}, 
                 embedding=[2, 4, 6], 
                 record=AirbyteRecordMessage(namespace=None, stream='example_stream', data={'str_col': 'Dogs are number 1', 'int_col': 10}, emitted_at=0))
        ],
    )
    assert(len(list(messages)) == 2)
    i = 1 
    for message in messages:
        message.type = "RECORD"
        assert message.record.data[METADATA_COLUMN] == {"_ab_stream": "abc"}
        assert message.record.data[DOCUMENT_CONTENT_COLUMN] == f"test{i}"
        assert message.record.data[EMBEDDING_COLUMN] == [1*i, 2*i, 3*i]
        assert all(key in message.record.data for key in [DOCUMENT_ID_COLUMN, CHUNK_ID_COLUMN])
        assert all(key not in message.record.data for key in ["str_col", "int_col"])
        i += 1


def test_add_columns_to_catalog():
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    updated_catalog = indexer._get_updated_catalog()
    # test all streams in catalog have the new columns
    for stream in updated_catalog.streams:
        assert all(column in stream.stream.json_schema["properties"] 
                   for column in [DOCUMENT_ID_COLUMN, CHUNK_ID_COLUMN, DOCUMENT_CONTENT_COLUMN, METADATA_COLUMN, EMBEDDING_COLUMN])
        if stream.stream.name in ['example_stream', 'example_stream2']:
            assert(stream.primary_key == [[DOCUMENT_ID_COLUMN]])
        if stream.stream.name == 'example_stream3':
            assert(stream.primary_key == [])


def test_get_primary_keys():
    # case: stream has one primary key 
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    assert(indexer._get_primary_keys('example_stream') == [['int_col']])
    
    # case: stream has no primary key
    catalog = generate_catalog()    
    catalog.streams[0].primary_key = None
    indexer = _create_snowflake_cortex_indexer(catalog)
    assert(indexer._get_primary_keys('example_stream') == None)

    # case: multiple primary keys
    catalog.streams[0].primary_key = [["int_col"], ["str_col"]]
    indexer = _create_snowflake_cortex_indexer(catalog)
    assert(indexer._get_primary_keys('example_stream') == [["int_col"], ["str_col"]])


def test_get_record_primary_key():
    # case: stream has one primary key = int_col
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    message = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="example_stream",
            data={
                'str_col': "Dogs are number 1",
                'int_col': 5,
                'page_content': "str_col: Dogs are number 1",
                'metadata': {"int_col": 5, "_ab_stream": "myteststream"},
                'embedding': [1, 2, 3, 4]
            },
            emitted_at=0,
        )
    )
    assert(indexer._get_record_primary_key(message) == "5")

    # case: stream has no primary key
    catalog = generate_catalog()    
    catalog.streams[0].primary_key = None
    indexer = _create_snowflake_cortex_indexer(catalog)
    assert(indexer._get_record_primary_key(message) == None)

    # case: multiple primary keys = [int_col, str_col]
    catalog.streams[0].primary_key = [["int_col"], ["str_col"]]
    indexer = _create_snowflake_cortex_indexer(catalog)
    assert(indexer._get_record_primary_key(message) == "5_Dogs are number 1")


def test_create_state_message():
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    airbyte_message = indexer._create_state_message("example_stream", "ns1", {"state": "1"} )
    assert airbyte_message.type == Type.STATE
    assert airbyte_message.state.data == {"state": "1"}
    state_msg = cast(AirbyteStateMessage, airbyte_message.state)
    stream_state = cast(AirbyteStreamState, state_msg.stream)
    assert stream_state.stream_descriptor.name == "example_stream"
    assert stream_state.stream_descriptor.namespace == "ns1"
    
def test_get_write_strategy():
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    assert(indexer.get_write_strategy('example_stream') == WriteStrategy.MERGE)
    assert(indexer.get_write_strategy('example_stream2') == WriteStrategy.APPEND)
    assert(indexer.get_write_strategy('example_stream3') == WriteStrategy.APPEND)

def test_get_document_id():
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    message = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="example_stream",
            data={
                'str_col': "Dogs are number 1",
                'int_col': 5,
                'page_content': "str_col: Dogs are number 1",
                'metadata': {"int_col": 5, "_ab_stream": "myteststream"},
                'embedding': [1, 2, 3, 4]
            },
            emitted_at=0,
        )
    )
    assert(indexer._create_document_id(message) == "Stream_example_stream_Key_5")

    catalog = generate_catalog()    
    catalog.streams[0].primary_key = None
    indexer = _create_snowflake_cortex_indexer(catalog)
    assert(indexer._create_document_id(message) != "Stream_example_stream_Key_5")

    catalog.streams[0].primary_key = [["int_col"], ["str_col"]]
    indexer = _create_snowflake_cortex_indexer(catalog)
    assert(indexer._create_document_id(message) == "Stream_example_stream_Key_5_Dogs are number 1")

def test_delete():
    delete_ids = [1, 2, 3]
    namespace = "test_namespace"
    stream = "test_stream"
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
        
    indexer.delete(delete_ids, namespace, stream)


def test_check():
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    mock_processor = MagicMock()
    indexer.default_processor = mock_processor
    mock_processor._get_tables_list.return_value = ["table1", "table2"]
    result = indexer.check()
    mock_processor._get_tables_list.assert_called_once()
    assert result == None


def test_pre_sync_table_does_exist():
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    mock_processor = MagicMock()
    indexer.default_processor = mock_processor
    
    mock_processor._get_tables_list.return_value = ["table1", "table2"]
    mock_processor._execute_query.return_value = None
    indexer.pre_sync(generate_catalog())
    mock_processor._get_tables_list.assert_called_once()
    mock_processor._execute_sql.assert_not_called()

def test_pre_sync_table_exists():
    indexer = _create_snowflake_cortex_indexer(generate_catalog())
    mock_processor = MagicMock()
    indexer.default_processor = mock_processor
   
    mock_processor._get_tables_list.return_value = ["example_stream2", "table2"]
    mock_processor._execute_query.return_value = None
    indexer.pre_sync(generate_catalog())
    mock_processor._get_tables_list.assert_called_once()
    mock_processor._execute_sql.assert_called_once()

def generate_catalog():
    return ConfiguredAirbyteCatalog.parse_obj(
        {
            "streams": [
                {
                    "stream": {
                        "name": "example_stream",
                        "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": False,
                        "default_cursor_field": ["column_name"],
                        "namespace": "ns1",
                    },
                    "primary_key": [["int_col"]],
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append_dedup",
                },
                {
                    "stream": {
                        "name": "example_stream2",
                        "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": False,
                        "default_cursor_field": ["column_name"],
                        "namespace": "ns2",
                    },
                    "primary_key": [["int_col"]],
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                },
                {
                    "stream": {
                        "name": "example_stream3",
                        "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": False,
                        "default_cursor_field": ["column_name"],
                        "namespace": "ns2",
                    },
                    "primary_key": [],
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                },
            ]
        }
    )
