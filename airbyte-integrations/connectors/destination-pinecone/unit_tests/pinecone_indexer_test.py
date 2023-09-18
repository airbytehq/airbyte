#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, MagicMock, Mock, call, patch

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_pinecone.config import PineconeIndexingModel
from destination_pinecone.indexer import PineconeIndexer
from pinecone import IndexDescription


def create_pinecone_indexer():
    config = PineconeIndexingModel(mode="pinecone", pinecone_environment="myenv", pinecone_key="mykey", index="myindex")
    indexer = PineconeIndexer(config, 3)

    indexer.pinecone_index.delete = MagicMock()
    indexer.pinecone_index.upsert = MagicMock()
    indexer.pinecone_index.query = MagicMock()
    return indexer


def create_index_description(dimensions=3, pod_type="p1"):
    return IndexDescription(
        name="",
        metric="",
        replicas=1,
        dimension=dimensions,
        shards=1,
        pods=1,
        pod_type=pod_type,
        status=None,
        metadata_config=None,
        source_collection=None,
    )


@pytest.fixture(scope="module", autouse=True)
def mock_describe_index():
    with patch("pinecone.describe_index") as mock:
        mock.return_value = create_index_description()
        yield mock


def test_pinecone_index_upsert_and_delete(mock_describe_index):
    indexer = create_pinecone_indexer()
    indexer._pod_type = "p1"
    indexer.index(
        [
            Mock(page_content="test", metadata={"_ab_stream": "abc"}, embedding=[1,2,3]),
            Mock(page_content="test2", metadata={"_ab_stream": "abc"}, embedding=[4,5,6]),
        ],
        ["delete_id1", "delete_id2"],
    )
    indexer.pinecone_index.delete.assert_called_with(filter={"_ab_record_id": {"$in": ["delete_id1", "delete_id2"]}})
    indexer.pinecone_index.upsert.assert_called_with(
        vectors=(
            (ANY, [1, 2, 3], {"_ab_stream": "abc", "text": "test"}),
            (ANY, [4, 5, 6], {"_ab_stream": "abc", "text": "test2"}),
        ),
        async_req=True,
        show_progress=False,
    )


def test_pinecone_index_upsert_and_delete_starter(mock_describe_index):
    indexer = create_pinecone_indexer()
    indexer._pod_type = "starter"
    indexer.pinecone_index.query.return_value = MagicMock(matches=[MagicMock(id="doc_id1"), MagicMock(id="doc_id2")])
    indexer.index(
        [
            Mock(page_content="test", metadata={"_ab_stream": "abc"}, embedding=[1,2,3]),
            Mock(page_content="test2", metadata={"_ab_stream": "abc"}, embedding=[4,5,6]),
        ],
        ["delete_id1", "delete_id2"],
    )
    indexer.pinecone_index.query.assert_called_with(
        vector=[0, 0, 0], filter={"_ab_record_id": {"$in": ["delete_id1", "delete_id2"]}}, top_k=10_000
    )
    indexer.pinecone_index.delete.assert_called_with(ids=["doc_id1", "doc_id2"])
    indexer.pinecone_index.upsert.assert_called_with(
        vectors=(
            (ANY, [1, 2, 3], {"_ab_stream": "abc", "text": "test"}),
            (ANY, [4, 5, 6], {"_ab_stream": "abc", "text": "test2"}),
        ),
        async_req=True,
        show_progress=False,
    )


def test_pinecone_index_delete_1k_limit(mock_describe_index):
    indexer = create_pinecone_indexer()
    indexer._pod_type = "starter"
    indexer.pinecone_index.query.return_value = MagicMock(matches=[MagicMock(id=f"doc_id_{str(i)}") for i in range(1300)])
    indexer.index(
        [],
        ["delete_id1"],
    )
    indexer.pinecone_index.delete.assert_has_calls([call(ids=[f"doc_id_{str(i)}" for i in range(1000)]), call(ids=[f"doc_id_{str(i+1000)}" for i in range(300)])])


def test_pinecone_index_empty_batch():
    indexer = create_pinecone_indexer()
    indexer.index(
        [],
        [],
    )
    indexer.pinecone_index.delete.assert_not_called()
    indexer.pinecone_index.upsert.assert_not_called()


def test_pinecone_index_upsert_batching():
    indexer = create_pinecone_indexer()
    indexer.index(
        [Mock(page_content=f"test {i}", metadata={"_ab_stream": "abc"}, embedding=[i,i,i]) for i in range(50)],
        [],
    )
    assert indexer.pinecone_index.upsert.call_count == 2
    for i in range(40):
        assert indexer.pinecone_index.upsert.call_args_list[0].kwargs["vectors"][i] == (
            ANY,
            [i, i, i],
            {"_ab_stream": "abc", "text": f"test {i}"},
        )
    for i in range(40, 50):
        assert indexer.pinecone_index.upsert.call_args_list[1].kwargs["vectors"][i - 40] == (
            ANY,
            [i, i, i],
            {"_ab_stream": "abc", "text": f"test {i}"},
        )


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


def test_pinecone_pre_sync(mock_describe_index):
    indexer = create_pinecone_indexer()
    indexer.pre_sync(generate_catalog())
    indexer.pinecone_index.delete.assert_called_with(filter={"_ab_stream": "example_stream2"})


def test_pinecone_pre_sync_starter(mock_describe_index):
    mock_describe_index.return_value = create_index_description(pod_type="starter")
    indexer = create_pinecone_indexer()
    indexer.pinecone_index.query.return_value = MagicMock(matches=[MagicMock(id="doc_id1"), MagicMock(id="doc_id2")])
    indexer.pre_sync(generate_catalog())
    indexer.pinecone_index.query.assert_called_with(vector=[0, 0, 0], filter={"_ab_stream": "example_stream2"}, top_k=10_000)
    indexer.pinecone_index.delete.assert_called_with(ids=["doc_id1", "doc_id2"])


@pytest.mark.parametrize(
    "describe_throws,reported_dimensions,check_succeeds",
    [
        (False, 3, True),
        (False, 4, False),
        (True, 3, False),
        (True, 4, False),
    ],
)
@patch("pinecone.describe_index")
def test_pinecone_check(describe_mock, describe_throws, reported_dimensions, check_succeeds):
    indexer = create_pinecone_indexer()
    indexer.embedding_dimensions = 3
    if describe_throws:
        describe_mock.side_effect = Exception("describe failed")
    describe_mock.return_value = create_index_description(dimensions=reported_dimensions)
    result = indexer.check()
    if check_succeeds:
        assert result is None
    else:
        assert result is not None


def test_metadata_normalization():
    indexer = create_pinecone_indexer()

    indexer._pod_type = "p1"
    indexer.index(
        [
            Mock(
                page_content="test",
                embedding=[1, 2, 3],
                metadata={
                    "_ab_stream": "abc",
                    "id": 1,
                    "a_complex_field": {"a_nested_field": "a_nested_value"},
                    "too_big": "a" * 40_000,
                    "small": "a",
                },
            ),
        ],
        [],
    )
    indexer.pinecone_index.upsert.assert_called_with(
        vectors=((ANY, [1, 2, 3], {"_ab_stream": "abc", "text": "test", "small": "a", "id": 1}),),
        async_req=True,
        show_progress=False,
    )
