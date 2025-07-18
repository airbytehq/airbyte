#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import ANY, MagicMock, Mock, patch

import pytest
import urllib3
from destination_astra.config import AstraIndexingModel
from destination_astra.indexer import AstraIndexer

from airbyte_cdk.models import ConfiguredAirbyteCatalog


def create_astra_indexer():
    config = AstraIndexingModel(
        astra_db_app_token="mytoken",
        astra_db_endpoint="https://8292d414-dd1b-4c33-8431-e838bedc04f7-us-east1.apps.astra.datastax.com",
        astra_db_keyspace="mykeyspace",
        collection="mycollection",
    )
    indexer = AstraIndexer(config, 3)

    indexer.client.delete_documents = MagicMock()
    indexer.client.insert_documents = MagicMock()
    indexer.client.find_documents = MagicMock()

    return indexer


def create_index_description(collection_name, dimensions):
    return {"name": collection_name, "options": {"vector": {"dimension": dimensions, "metric": "cosine"}}}


def test_astra_index_upsert_and_delete():
    indexer = create_astra_indexer()
    indexer.index(
        [
            Mock(page_content="test", metadata={"_ab_stream": "abc"}, embedding=[1, 2, 3]),
            Mock(page_content="test2", metadata={"_ab_stream": "abc"}, embedding=[4, 5, 6]),
        ],
        "ns1",
        "some_stream",
    )
    indexer.delete(["delete_id1", "delete_id2"], "ns1", "some_stram")
    indexer.client.delete_documents.assert_called_with(
        collection_name="mycollection", filter={"_ab_record_id": {"$in": ["delete_id1", "delete_id2"]}}
    )
    indexer.client.insert_documents.assert_called_with(
        collection_name="mycollection",
        documents=[
            {"_id": ANY, "$vector": [1, 2, 3], "_ab_stream": "abc", "text": "test"},
            {"_id": ANY, "$vector": [4, 5, 6], "_ab_stream": "abc", "text": "test2"},
        ],
    )


def test_astra_index_empty_batch():
    indexer = create_astra_indexer()
    indexer.index([], "ns1", "some_stream")
    indexer.client.delete_documents.assert_not_called()
    indexer.client.insert_documents.assert_not_called()


def test_astra_index_upsert_batching():
    indexer = create_astra_indexer()
    indexer.index(
        [Mock(page_content=f"test {i}", metadata={"_ab_stream": "abc"}, embedding=[i, i, i]) for i in range(50)],
        "ns1",
        "some_stream",
    )
    assert indexer.client.insert_documents.call_count == 3
    for i in range(20):
        assert indexer.client.insert_documents.call_args_list[0].kwargs.get("documents")[i] == {
            "_id": ANY,
            "$vector": [i, i, i],
            "_ab_stream": "abc",
            "text": f"test {i}",
        }
    for i in range(20, 40):
        assert indexer.client.insert_documents.call_args_list[1].kwargs.get("documents")[i - 20] == {
            "_id": ANY,
            "$vector": [i, i, i],
            "_ab_stream": "abc",
            "text": f"test {i}",
        }
    for i in range(40, 50):
        assert indexer.client.insert_documents.call_args_list[2].kwargs.get("documents")[i - 40] == {
            "_id": ANY,
            "$vector": [i, i, i],
            "_ab_stream": "abc",
            "text": f"test {i}",
        }


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
                    "primary_key": [["_id"]],
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
                    "primary_key": [["_id"]],
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                },
            ]
        }
    )


def test_astra_pre_sync():
    indexer = create_astra_indexer()
    indexer.client.find_collection = MagicMock(collection_name="")
    indexer.client.find_collection.return_value = True

    indexer.pre_sync(generate_catalog())
    indexer.client.delete_documents.assert_called_with(collection_name="mycollection", filter={"_ab_stream": "ns2_example_stream2"})


@pytest.mark.parametrize(
    "collection_name,describe_throws,reported_dimensions,check_succeeds,error_message",
    [
        ("mycollection", None, 3, True, None),
        ("other_collection", None, 3, False, "mycollection collection does not exist."),
        (
            ["mycollection"],
            urllib3.exceptions.MaxRetryError(
                None, "", reason=Exception("Failed to resolve environment, please check whether the credential is correct.")
            ),
            3,
            False,
            "Failed to resolve environment",
        ),
        ("mycollection", None, 4, False, "Make sure embedding and indexing configurations match."),
        ("mycollection", Exception("describe failed"), 3, False, "describe failed"),
        ("mycollection", Exception("describe failed"), 4, False, "describe failed"),
    ],
)
def test_astra_check(collection_name, describe_throws, reported_dimensions, check_succeeds, error_message):
    indexer = create_astra_indexer()

    indexer.client.create_collection = MagicMock()
    indexer.client.find_collections = MagicMock()
    indexer.client.find_collections.return_value = [
        create_index_description(collection_name=collection_name, dimensions=reported_dimensions)
    ]

    if describe_throws:
        indexer.client.find_collections.side_effect = describe_throws
    else:
        indexer.client.find_collections.return_value = [
            create_index_description(collection_name=collection_name, dimensions=reported_dimensions)
        ]

    result = indexer.check()
    if check_succeeds:
        assert result is None
    else:
        assert error_message in result
