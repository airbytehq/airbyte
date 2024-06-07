#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
from typing import Any, Iterable, Mapping

import pika
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type
from pika.adapters.blocking_connection import BlockingConnection
from pika.spec import BasicProperties

_DEFAULT_PORT = 5672


def create_connection(config: Mapping[str, Any]) -> BlockingConnection:
    host = config.get("host")
    port = config.get("port") or _DEFAULT_PORT
    username = config.get("username")
    password = config.get("password")
    virtual_host = config.get("virtual_host", "")
    ssl_enabled = config.get("ssl", False)
    amqp_protocol = "amqp"
    host_url = host
    if ssl_enabled:
        amqp_protocol = "amqps"
    if port:
        host_url = host + ":" + str(port)
    credentials = f"{username}:{password}@" if username and password else ""
    params = pika.URLParameters(f"{amqp_protocol}://{credentials}{host_url}/{virtual_host}")
    return BlockingConnection(params)


class DestinationRabbitmq(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        exchange = config.get("exchange")
        routing_key = config["routing_key"]
        connection = create_connection(config=config)
        channel = connection.channel()

        streams = {s.stream.name for s in configured_catalog.streams}
        try:
            for message in input_messages:
                if message.type == Type.STATE:
                    # Emitting a state message means all records that came before it
                    # have already been published.
                    yield message
                elif message.type == Type.RECORD:
                    record = message.record
                    if record.stream not in streams:
                        # Message contains record from a stream that is not in the catalog. Skip it!
                        continue
                    headers = {"stream": record.stream, "emitted_at": record.emitted_at, "namespace": record.namespace}
                    properties = BasicProperties(content_type="application/json", headers=headers)
                    channel.basic_publish(
                        exchange=exchange or "", routing_key=routing_key, properties=properties, body=json.dumps(record.data)
                    )
                else:
                    # Let's ignore other message types for now
                    continue
        finally:
            connection.close()

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            connection = create_connection(config=config)
        except Exception as e:
            logger.error(f"Failed to create connection. Error: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Could not create connection: {repr(e)}")
        try:
            channel = connection.channel()
            if channel.is_open:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            return AirbyteConnectionStatus(status=Status.FAILED, message="Could not open channel")
        except Exception as e:
            logger.error(f"Failed to open RabbitMQ channel. Error: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
        finally:
            connection.close()
