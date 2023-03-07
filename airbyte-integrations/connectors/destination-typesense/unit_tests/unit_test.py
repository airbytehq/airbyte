#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from destination_typesense.writer import TypesenseWriter


@patch("typesense.Client")
def test_queue_write_operation(client):
    writer = TypesenseWriter(client, "steam_name")
    writer.queue_write_operation({"a": "a"})
    assert len(writer.write_buffer) == 1


@patch("typesense.Client")
def test_flush(client):
    writer = TypesenseWriter(client, "steam_name")
    writer.queue_write_operation({"a": "a"})
    writer.flush()
    client.collections.__getitem__.assert_called_once_with("steam_name")
