#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, call

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_langchain.config import ChromaLocalIndexingModel
from destination_langchain.indexer import ChromaLocalIndexer
from langchain.document_loaders.base import Document


def create_chroma_local_indexer():
    config = ChromaLocalIndexingModel(mode="chroma_local", destination_path="/test", collection_name="myindex")
    embedder = MagicMock()
    indexer = ChromaLocalIndexer(config, embedder)

    indexer.vectorstore = MagicMock()
    indexer.vectorstore._collection = MagicMock()
    indexer.vectorstore._collection.delete = MagicMock()
    indexer.embed_fn = MagicMock(return_value=[[1, 2, 3], [4, 5, 6]])
    indexer.vectorstore.add_documents = MagicMock()
    return indexer


def test_chroma_local_index_upsert_and_delete():
    indexer = create_chroma_local_indexer()
    docs = [
        Document(page_content="test", metadata={"_airbyte_stream": "abc"}),
        Document(page_content="test2", metadata={"_airbyte_stream": "abc"}),
    ]
    indexer.index(
        docs,
        ["delete_id1", "delete_id2"],
    )
    indexer.vectorstore._collection.delete.assert_has_calls(
        [
            call(where={"_record_id": {"$eq": "delete_id1"}}),
            call(where={"_record_id": {"$eq": "delete_id2"}}),
        ]
    )
    indexer.vectorstore.add_documents.assert_called_with(docs)


def test_chroma_local_normalize_metadata():
    indexer = create_chroma_local_indexer()
    docs = [
        Document(page_content="test", metadata={"_airbyte_stream": "abc", "a_boolean_value": True}),
    ]
    indexer.index(
        docs,
        [],
    )
    indexer.vectorstore.add_documents.assert_called_with([
        Document(page_content="test", metadata={"_airbyte_stream": "abc", "a_boolean_value": "True"}),
    ])


def test_chroma_local_index_empty_batch():
    indexer = create_chroma_local_indexer()
    indexer.index(
        [],
        [],
    )
    indexer.vectorstore._collection.delete.assert_not_called()
    indexer.vectorstore.add_documents.assert_called_with([])


def test_chroma_local_pre_sync():
    indexer = create_chroma_local_indexer()
    indexer._init_vectorstore = MagicMock()
    indexer.pre_sync(
        ConfiguredAirbyteCatalog.parse_obj(
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
                    },
                    {
                        "stream": {
                            "name": "example_stream2",
                            "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                            "supported_sync_modes": ["full_refresh", "incremental"],
                            "source_defined_cursor": False,
                            "default_cursor_field": ["column_name"],
                        },
                        "primary_key": [["id"]],
                        "sync_mode": "full_refresh",
                        "destination_sync_mode": "overwrite",
                    },
                ]
            }
        )
    )
    indexer._init_vectorstore.assert_called()
    indexer.vectorstore._collection.delete.assert_called_with(where={"_airbyte_stream": {"$eq": "example_stream2"}})
