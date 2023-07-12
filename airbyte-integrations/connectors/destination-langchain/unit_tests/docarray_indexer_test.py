#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, patch

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_langchain.config import DocArrayHnswSearchIndexingModel
from destination_langchain.indexer import DocArrayHnswSearchIndexer
from langchain.document_loaders.base import Document


class DocArrayIndexerTest(unittest.TestCase):
    def setUp(self):
        self.config = DocArrayHnswSearchIndexingModel(mode="DocArrayHnswSearch", destination_path="/tmp/made_up")
        self.embedder = MagicMock()
        self.embedder.embedding_dimensions = 3
        self.indexer = DocArrayHnswSearchIndexer(self.config, self.embedder)
        self.indexer.vectorstore = MagicMock()

    def test_docarray_index(self):
        docs = [
            Document(page_content="test", metadata={"_airbyte_stream": "abc"}),
            Document(page_content="test2", metadata={"_airbyte_stream": "abc"}),
        ]

        self.indexer.index(
            docs,
            ["delete_id1", "delete_id2"],
        )
        # deleted documents are ignored
        self.indexer.vectorstore.add_documents.assert_called_with(docs)

    def test_docarray_pre_sync_fail(self):
        try:
            self.indexer.pre_sync(ConfiguredAirbyteCatalog.parse_obj(
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
                    ]
                }
            ))
            assert False, "Expected exception"
        except Exception as e:
            assert str(e) == "DocArrayHnswSearchIndexer only supports overwrite mode, got DestinationSyncMode.append_dedup for stream example_stream"

    @patch('os.listdir')
    @patch('os.remove')
    def test_docarray_pre_sync_succeed(self, remove_mock, listdir_mock):
        listdir_mock.return_value = ["file1", "file2"]
        self.indexer._init_vectorstore = MagicMock()
        self.indexer.pre_sync(ConfiguredAirbyteCatalog.parse_obj(
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
                        "sync_mode": "full_refresh",
                        "destination_sync_mode": "overwrite",
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
        ))
        assert remove_mock.call_count == 2
        assert self.indexer._init_vectorstore.call_count == 1
