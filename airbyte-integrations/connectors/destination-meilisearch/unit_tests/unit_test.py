#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from destination_meilisearch.writer import MeiliWriter


@patch("meilisearch.Client")
def test_queue_write_operation(client):
    writer = MeiliWriter(client, "steam_name", "primary_key")
    writer.queue_write_operation({"a": "a"})
    assert len(writer.write_buffer) == 1


@patch("meilisearch.Client")
def test_flush(client):
    writer = MeiliWriter(client, "steam_name", "primary_key")
    writer.queue_write_operation({"a": "a"})
    writer.flush()
    client.index.assert_called_once_with("steam_name")
    client.wait_for_task.assert_called_once()
