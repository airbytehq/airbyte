#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from destination_meilisearch.writer import MeiliWriter


@patch("meilisearch.Client")
def test_queue_write_operation(client):
    writer = MeiliWriter(client, "stream_name", "primary_key")
    writer.queue_write_operation({"a": "a"})
    assert len(writer._write_buffer) == 1
    writer.queue_write_operation({"b": "b"})
    assert len(writer._write_buffer) == 2
    writer2 = MeiliWriter(client, "stream_name2", "primary_key")
    writer2.queue_write_operation({"a": "a"})
    assert len(writer2._write_buffer) == 1
    assert len(writer._write_buffer) == 2


@patch("meilisearch.Client")
def test_flush(client):
    writer = MeiliWriter(client, "stream_name", "primary_key")
    writer.queue_write_operation({"a": "a"})
    writer.flush()
    client.index.assert_called_once_with("stream_name")
    client.wait_for_task.assert_called_once()
