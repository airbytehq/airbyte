#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dataclasses
import io
import logging
import time
from typing import Any, Iterable, List, Mapping

import orjson
from typesense import Client

from airbyte_cdk.destinations import Destination
from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    DestinationSyncMode,
    Status,
    Type,
)
from destination_typesense.writer import TypesenseWriter


logger = logging.getLogger("airbyte")

_STATE_ADDITIONAL_PROPERTIES_ATTR = "_airbyte_additional_properties"
_AIRBYTE_STATE_MESSAGE_WIRE_KEYS = {
    "global" if field.name == "global_" else field.name for field in dataclasses.fields(AirbyteStateMessage)
}


def serialize_airbyte_message(message: AirbyteMessage) -> dict[str, Any]:
    """Work around airbytehq/airbyte-python-cdk#1134 until the CDK preserves state extras."""
    serialized_message = AirbyteMessageSerializer.dump(message)
    if message.type == Type.STATE and message.state is not None:
        additional_properties = getattr(message.state, _STATE_ADDITIONAL_PROPERTIES_ATTR, {})
        if additional_properties:
            state = serialized_message.setdefault("state", {})
            for key, value in additional_properties.items():
                state.setdefault(key, value)
    return serialized_message


def get_client(config: Mapping[str, Any]) -> Client:
    hosts = config.get("host").split(",")
    path = config.get("path")
    nodes = []
    for host in hosts:
        node = {
            "host": host,
            "port": config.get("port") or "8108",
            "protocol": config.get("protocol") or "https",
        }
        if path:
            node["path"] = path
        nodes.append(node)
    client = Client(
        {
            "api_key": config.get("api_key"),
            "nodes": nodes,
            "connection_timeout_seconds": 3600,
        }
    )

    return client


class DestinationTypesense(Destination):
    def _parse_input_stream(self, input_stream: io.TextIOWrapper) -> Iterable[AirbyteMessage]:
        """Preserve state extras until airbytehq/airbyte-python-cdk#1134 is fixed upstream."""
        for line in input_stream:
            try:
                raw = orjson.loads(line)
            except orjson.JSONDecodeError:
                logger.info(f"ignoring input which can't be deserialized as Airbyte Message: {line}")
                continue

            message = AirbyteMessageSerializer.load(raw)
            if message.type == Type.STATE and isinstance(raw.get("state"), dict) and message.state is not None:
                additional_properties = {key: value for key, value in raw["state"].items() if key not in _AIRBYTE_STATE_MESSAGE_WIRE_KEYS}
                if additional_properties:
                    setattr(message.state, _STATE_ADDITIONAL_PROPERTIES_ATTR, additional_properties)
            yield message

    def run(self, args: List[str]) -> None:
        init_uncaught_exception_handler(logger)
        parsed_args = self.parse_args(args)
        output_messages = self.run_cmd(parsed_args)
        for message in output_messages:
            print(orjson.dumps(serialize_airbyte_message(message)).decode())

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
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

            writer = TypesenseWriter(client, config.get("batch_size", 10000))
            writer.queue_write_operation("_airbyte", {"id": "1", "title": "The Hunger Games"})
            writer.flush()

            time.sleep(3)
            client.collections["_airbyte"].documents["1"].retrieve()

            status = AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            status = AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
        finally:
            try:
                client = get_client(config=config)
                client.collections["_airbyte"].delete()
            except Exception:
                logger.warning("Failed to delete _airbyte collection")

        return status
