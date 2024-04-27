#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, MagicMock, Mock, call, patch

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_snowflake_cortex.config import SnowflakeCortexIndexingModel
from destination_snowflake_cortex.indexer import (
    SnowflakeCortexIndexer,
    EMBEDDING_COLUMN,
    METADATA_COLUMN,
    PAGE_CONTENT_COLUMN,
    DOCUMENT_ID_COLUMN,
    CHUNK_ID_COLUMN
)
from airbyte_cdk.models import (
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    AirbyteMessage,
    Type,
)

@pytest.fixture(scope="module", autouse=True)
def mock_processor():
    with patch("airbyte._processors.sql.snowflake.SnowflakeSqlProcessor") as mock:
        mock.return_value = None
        yield mock

def _create_snowflake_cortex_indexer(mock_processor, catalog:ConfiguredAirbyteCatalog | None = None ):
    config = SnowflakeCortexIndexingModel(account="account", username="username", password="password", database="database", warehouse="warehouse", role="role")
    indexer = SnowflakeCortexIndexer(config, 3, Mock(ConfiguredAirbyteCatalog) if catalog is None else catalog)
    # TODO: figure how to mock SnowflakeSqlProcessor
    # assert mock_processor.called
    return indexer 
    

def test_get_airbyte_messsages_from_chunks(mock_processor):
    indexer = _create_snowflake_cortex_indexer(mock_processor)
    messages = indexer._get_airbyte_messsages_from_chunks(
        [
            Mock(page_content="test1", 
                 metadata={"_ab_stream": "abc"}, 
                 embedding=[1, 2, 3], 
                 record=AirbyteRecordMessage(namespace=None, stream='myteststream', data={'str_col': 'Dogs are number 0', 'int_col': 0}, emitted_at=0)),
            Mock(page_content="test2", 
                 metadata={"_ab_stream": "abc"}, 
                 embedding=[2, 4, 6], 
                 record=AirbyteRecordMessage(namespace=None, stream='myteststream', data={'str_col': 'Dogs are number 0', 'int_col': 0}, emitted_at=0))
        ],
    )
    assert(len(list(messages)) == 2)
    i = 1 
    for message in messages:
        message.type = "RECORD"
        assert message.data[METADATA_COLUMN] == {"_ab_stream": "abc"}
        assert message.data[PAGE_CONTENT_COLUMN] == f"test{i}"
        assert message.data[EMBEDDING_COLUMN] == [1*i, 2*i, 3*i]
        assert all(key in message.data for key in [DOCUMENT_ID_COLUMN, CHUNK_ID_COLUMN]) and all(key not in message.data for key in ["str_col", "int_col"])
        i += 1
        print(f"\nmessage --> {message}")


def test_add_columns_to_catalog(mock_processor):
    indexer = _create_snowflake_cortex_indexer(mock_processor, generate_catalog())
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
    updated_catalog = indexer._get_updated_catalog()
    # test all streams in catalog have the new columns
    for stream in updated_catalog.streams:
        assert all(column in stream.stream.json_schema["properties"] 
                   for column in [DOCUMENT_ID_COLUMN, CHUNK_ID_COLUMN, PAGE_CONTENT_COLUMN, METADATA_COLUMN, EMBEDDING_COLUMN])
        assert(stream.primary_key == [[DOCUMENT_ID_COLUMN]])

  

def test_get_primary_keys(mock_processor):
    indexer = _create_snowflake_cortex_indexer(mock_processor, generate_catalog())
    print(indexer._get_primary_keys('example_stream') )


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
            ]
        }
    )
