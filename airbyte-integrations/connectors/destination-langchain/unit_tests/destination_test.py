#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from airbyte_cdk.models.airbyte_protocol import AirbyteMessage, AirbyteRecordMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog, Type
from destination_langchain.config import ConfigModel
from destination_langchain.destination import DestinationLangchain, embedder_map, indexer_map


@patch.dict(embedder_map, {"openai": MagicMock()})
@patch.dict(indexer_map, {"pinecone": MagicMock()})
def test_write():
    """
    Basic test for the write method, batcher and document processor.
    """
    config = {
        "processing": {"text_fields": ["column_name"], "chunk_size": 1000},
        "embedding": {"mode": "openai", "openai_key": "mykey"},
        "indexing": {
            "mode": "pinecone",
            "pinecone_key": "mykey",
            "index": "myindex",
            "pinecone_environment": "myenv",
        },
    }
    config_model = ConfigModel.parse_obj(config)

    configured_catalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog.parse_obj(
        {
            "streams": [
                {
                    "stream": {
                        "name": "example_stream",
                        "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": False,
                        "default_cursor_field": ["column_name"],
                    },
                    "primary_key": [["id"]],
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append_dedup",
                }
            ]
        }
    )
    input_messages = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="example_stream", emitted_at=1234, data={"column_name": f"value {i}", "id": i}))
        for i in range(32 + 5)
    ]
    input_messages.append(AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage()))

    mock_embedder = MagicMock()
    embedder_map["openai"].return_value = mock_embedder

    mock_indexer = MagicMock()
    indexer_map["pinecone"].return_value = mock_indexer
    mock_indexer.max_metadata_size = 1000

    # Create the DestinationLangchain instance
    destination = DestinationLangchain()

    output_messages = destination.write(config, configured_catalog, input_messages)
    next(output_messages)

    embedder_map["openai"].assert_called_with(config_model.embedding)
    indexer_map["pinecone"].assert_called_with(config_model.indexing, mock_embedder)
    mock_indexer.pre_sync.assert_called_with(configured_catalog)
    # 2 batches
    assert len(mock_indexer.index.call_args) == 2
    try:
        next(output_messages)
    except StopIteration:
        pass
    mock_indexer.post_sync.assert_called()
