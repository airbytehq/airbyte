#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, MagicMock, Mock, call, patch

import pytest
import urllib3
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_pinecone.config import PineconeIndexingModel
from destination_pinecone.indexer import PineconeIndexer
from pinecone import IndexDescription, exceptions


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
            Mock(page_content="test", metadata={"_ab_stream": "abc"}, embedding=[1, 2, 3]),
            Mock(page_content="test2", metadata={"_ab_stream": "abc"}, embedding=[4, 5, 6]),
        ],
        "ns1",
        "some_stream",
    )
    indexer.delete(["delete_id1", "delete_id2"], "ns1", "some_stram")
    indexer.pinecone_index.delete.assert_called_with(filter={"_ab_record_id": {"$in": ["delete_id1", "delete_id2"]}}, namespace="ns1")
    indexer.pinecone_index.upsert.assert_called_with(
        vectors=(
            (ANY, [1, 2, 3], {"_ab_stream": "abc", "text": "test"}),
            (ANY, [4, 5, 6], {"_ab_stream": "abc", "text": "test2"}),
        ),
        async_req=True,
        show_progress=False,
        namespace="ns1",
    )


def test_pinecone_index_upsert_and_delete_starter(mock_describe_index):
    indexer = create_pinecone_indexer()
    indexer._pod_type = "starter"
    indexer.pinecone_index.query.side_effect = [
        MagicMock(matches=[MagicMock(id="doc_id1"), MagicMock(id="doc_id2")]),
        MagicMock(matches=[MagicMock(id="doc_id3")]),
        MagicMock(matches=[]),
    ]
    indexer.index(
        [
            Mock(page_content="test", metadata={"_ab_stream": "abc"}, embedding=[1, 2, 3]),
            Mock(page_content="test2", metadata={"_ab_stream": "abc"}, embedding=[4, 5, 6]),
        ],
        "ns1",
        "some_stream",
    )
    indexer.delete(["delete_id1", "delete_id2"], "ns1", "some_stram")
    indexer.pinecone_index.query.assert_called_with(
        vector=[0, 0, 0], filter={"_ab_record_id": {"$in": ["delete_id1", "delete_id2"]}}, top_k=10_000, namespace="ns1"
    )
    indexer.pinecone_index.delete.assert_has_calls(
        [call(ids=["doc_id1", "doc_id2"], namespace="ns1"), call(ids=["doc_id3"], namespace="ns1")]
    )
    indexer.pinecone_index.upsert.assert_called_with(
        vectors=(
            (ANY, [1, 2, 3], {"_ab_stream": "abc", "text": "test"}),
            (ANY, [4, 5, 6], {"_ab_stream": "abc", "text": "test2"}),
        ),
        async_req=True,
        show_progress=False,
        namespace="ns1",
    )


def test_pinecone_index_delete_1k_limit(mock_describe_index):
    indexer = create_pinecone_indexer()
    indexer._pod_type = "starter"
    indexer.pinecone_index.query.side_effect = [
        MagicMock(matches=[MagicMock(id=f"doc_id_{str(i)}") for i in range(1300)]),
        MagicMock(matches=[]),
    ]
    indexer.delete(["delete_id1"], "ns1", "some_stream")
    indexer.pinecone_index.delete.assert_has_calls(
        [
            call(ids=[f"doc_id_{str(i)}" for i in range(1000)], namespace="ns1"),
            call(ids=[f"doc_id_{str(i+1000)}" for i in range(300)], namespace="ns1"),
        ]
    )


def test_pinecone_index_empty_batch():
    indexer = create_pinecone_indexer()
    indexer.index([], "ns1", "some_stream")
    indexer.pinecone_index.delete.assert_not_called()
    indexer.pinecone_index.upsert.assert_not_called()


def test_pinecone_index_upsert_batching():
    indexer = create_pinecone_indexer()
    indexer.index(
        [Mock(page_content=f"test {i}", metadata={"_ab_stream": "abc"}, embedding=[i, i, i]) for i in range(50)],
        "ns1",
        "some_stream",
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
                        "namespace": "ns1",
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
                        "namespace": "ns2",
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
    indexer.pinecone_index.delete.assert_called_with(filter={"_ab_stream": "ns2_example_stream2"}, namespace="ns2")


def test_pinecone_pre_sync_starter(mock_describe_index):
    mock_describe_index.return_value = create_index_description(pod_type="starter")
    indexer = create_pinecone_indexer()
    indexer.pinecone_index.query.side_effect = [
        MagicMock(matches=[MagicMock(id="doc_id1"), MagicMock(id="doc_id2")]),
        MagicMock(matches=[]),
    ]
    indexer.pre_sync(generate_catalog())
    indexer.pinecone_index.query.assert_called_with(
        vector=[0, 0, 0], filter={"_ab_stream": "ns2_example_stream2"}, top_k=10_000, namespace="ns2"
    )
    indexer.pinecone_index.delete.assert_called_with(ids=["doc_id1", "doc_id2"], namespace="ns2")


@pytest.mark.parametrize(
    "index_list, describe_throws,reported_dimensions,check_succeeds, error_message",
    [
        (["myindex"], None, 3, True, None),
        (["other_index"], None, 3, False, "Index myindex does not exist in environment"),
        (
            ["myindex"],
            urllib3.exceptions.MaxRetryError(None, "", reason=Exception("Failed to resolve 'controller.myenv.pinecone.io'")),
            3,
            False,
            "Failed to resolve environment",
        ),
        (["myindex"], exceptions.UnauthorizedException(http_resp=urllib3.HTTPResponse(body="No entry!")), 3, False, "No entry!"),
        (["myindex"], None, 4, False, "Make sure embedding and indexing configurations match."),
        (["myindex"], Exception("describe failed"), 3, False, "describe failed"),
        (["myindex"], Exception("describe failed"), 4, False, "describe failed"),
    ],
)
@patch("pinecone.describe_index")
@patch("pinecone.list_indexes")
def test_pinecone_check(list_mock, describe_mock, index_list, describe_throws, reported_dimensions, check_succeeds, error_message):
    indexer = create_pinecone_indexer()
    indexer.embedding_dimensions = 3
    if describe_throws:
        describe_mock.side_effect = describe_throws
    else:
        describe_mock.return_value = create_index_description(dimensions=reported_dimensions)
    list_mock.return_value = index_list
    result = indexer.check()
    if check_succeeds:
        assert result is None
    else:
        assert error_message in result


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
        None,
        "some_stream",
    )
    indexer.pinecone_index.upsert.assert_called_with(
        vectors=((ANY, [1, 2, 3], {"_ab_stream": "abc", "text": "test", "small": "a", "id": 1}),),
        async_req=True,
        show_progress=False,
        namespace=None,
    )
