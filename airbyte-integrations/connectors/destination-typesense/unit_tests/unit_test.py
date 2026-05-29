#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

import pytest
from destination_typesense.writer import TypesenseWriter
from typesense.exceptions import ObjectAlreadyExists, ObjectNotFound

from airbyte_cdk import AirbyteTracedException


@patch("typesense.Client")
def test_default_batch_size(client):
    writer = TypesenseWriter(client)
    assert writer.batch_size == 10000


@patch("typesense.Client")
def test_empty_batch_size(client):
    writer = TypesenseWriter(client, "")
    assert writer.batch_size == 10000


@patch("typesense.Client")
def test_custom_batch_size(client):
    writer = TypesenseWriter(client, 9000)
    assert writer.batch_size == 9000


@patch("typesense.Client")
def test_queue_write_operation(client):
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})
    assert len(writer.write_buffer) == 1


@patch("typesense.Client")
def test_flush(client):
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})
    writer.flush()
    client.collections.__getitem__.assert_called_once_with("stream_name")


@patch("typesense.Client")
def test_flush_creates_missing_collection_before_retrying_import(client):
    client.collections.__getitem__.return_value.documents.import_.side_effect = [
        ObjectNotFound(404, "Collection not found"),
        None,
    ]
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})

    writer.flush()

    client.collections.create.assert_called_once_with({"name": "stream_name", "fields": [{"name": ".*", "type": "auto"}]})
    assert client.collections.__getitem__.return_value.documents.import_.call_count == 2


@patch("typesense.Client")
def test_flush_retries_import_when_missing_collection_is_created_by_another_writer(client):
    client.collections.create.side_effect = ObjectAlreadyExists(409, "Collection already exists")
    client.collections.__getitem__.return_value.documents.import_.side_effect = [
        ObjectNotFound(404, "Collection not found"),
        None,
    ]
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})

    writer.flush()

    client.collections.create.assert_called_once_with({"name": "stream_name", "fields": [{"name": ".*", "type": "auto"}]})
    assert client.collections.__getitem__.return_value.documents.import_.call_count == 2


@patch("typesense.Client")
def test_flush_raises_traced_exception_when_collection_remains_unavailable(client):
    client.collections.__getitem__.return_value.documents.import_.side_effect = ObjectNotFound(
        404,
        "Collection not found",
    )
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})

    with pytest.raises(AirbyteTracedException) as exc_info:
        writer.flush()

    assert exc_info.value.message == "Typesense collection is unavailable for document import."
