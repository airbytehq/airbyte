#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


def test_example_method():
    assert True


from unittest.mock import MagicMock, call

from destination_astra.astra_client import AstraClient


def create_astra_client():
    client = AstraClient("https://astra-endpoint", "token", "keyspace", 3, "cosine")
    client._run_query = MagicMock()
    return client


def test_delete_documents_single_batch():
    client = create_astra_client()
    client._run_query.return_value = {"status": {"deletedCount": 5}}

    assert client.delete_documents("mycollection", {"_ab_stream": "abc"}) == 5
    client._run_query.assert_called_once_with(
        "https://astra-endpoint/api/json/v1/keyspace/mycollection", {"deleteMany": {"filter": {"_ab_stream": "abc"}}}
    )


def test_delete_documents_pages_until_no_more_data():
    client = create_astra_client()
    client._run_query.side_effect = [
        {"status": {"deletedCount": 20, "moreData": True}},
        {"status": {"deletedCount": 20, "moreData": True}},
        {"status": {"deletedCount": 7}},
    ]

    assert client.delete_documents("mycollection", {"_ab_stream": "abc"}) == 47
    assert client._run_query.call_count == 3
    assert (
        client._run_query.call_args_list
        == [call("https://astra-endpoint/api/json/v1/keyspace/mycollection", {"deleteMany": {"filter": {"_ab_stream": "abc"}}})] * 3
    )
