#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import time
from typing import Any, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_typesense.writer import TypesenseWriter
from typesense import Client


def get_client(config: Mapping[str, Any]) -> Client:
    hosts = config.get("host").split(",")
    path = config.get("path")
    nodes = []
    for host in hosts:
        node = {"host": host, "port": config.get("port") or "8108", "protocol": config.get("protocol") or "https"}
        if path:
            node["path"] = path
        nodes.append(node)
    client = Client({"api_key": config.get("api_key"), "nodes": nodes, "connection_timeout_seconds": 3600})

    return client


class DestinationTypesense(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        client = get_client(config=config)

        for configured_stream in configured_catalog.streams:
            steam_name = configured_stream.stream.name
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                try:
                    client.collections[steam_name].delete()
                except Exception:
                    pass
                client.collections.create({"name": steam_name, "fields": [{"name": ".*", "type": "auto"}]})

        writer = TypesenseWriter(client, config.get("batch_size"))
        for message in input_messages:
            if message.type == Type.STATE:
                writer.flush()
                yield message
            elif message.type == Type.RECORD:
                record = message.record
                writer.queue_write_operation(record.stream, record.data)
            else:
                continue
        writer.flush()

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        logger.debug("TypeSense Destination Config Check")
        try:
            client = get_client(config=config)
            client.collections.create({"name": "_airbyte", "fields": [{"name": "title", "type": "string"}]})
            client.collections["_airbyte"].documents.create({"id": "1", "title": "The Hunger Games"})
            time.sleep(3)
            client.collections["_airbyte"].documents["1"].retrieve()
            client.collections["_airbyte"].delete()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
