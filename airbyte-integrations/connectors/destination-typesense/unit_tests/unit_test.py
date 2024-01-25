#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from destination_typesense.writer import TypesenseWriter


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
