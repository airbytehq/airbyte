#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Mapping, Any, Iterable

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, ConfiguredAirbyteCatalog, AirbyteMessage, Status, Type

import json
import pika
from pika.adapters.blocking_connection import BlockingConnection
from pika.spec import BasicProperties
from pika.credentials import PlainCredentials

_DEFAULT_PORT = 5672


def create_connection(config: Mapping[str, Any]) -> BlockingConnection:
    username = config.get('username')
    password = config.get('password')
    virtual_host = config.get('virtual_host')
    params = pika.ConnectionParameters(
        host=config['host'],
        port=config.get('port') or _DEFAULT_PORT
    )
    if username and password:
        params.credentials = PlainCredentials(username=username, password=password)
    if virtual_host:
        params.virtual_host = virtual_host
    return BlockingConnection(params)


class DestinationRabbitmq(Destination):
    def write(
            self,
            config: Mapping[str, Any],
            configured_catalog: ConfiguredAirbyteCatalog,
            input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        exchange = config.get('exchange')
        routing_key = config['routing_key']
        connection = create_connection(config=config)
        channel = connection.channel()

        try:
            for message in input_messages:
                if message.type == Type.STATE:
                    # Emitting a state message means all records that came before it 
                    # have already been published.
                    yield message
                elif message.type == Type.RECORD:
                    record = message.record
                    headers = {'stream': record.stream, 'emitted_at': record.emitted_at, 'namespace': record.namespace}
                    properties = BasicProperties(content_type='application/json', headers=headers)
                    channel.basic_publish(exchange=exchange or '',
                                          routing_key=routing_key,
                                          properties=properties,
                                          body=json.dumps(record.data))
                else:
                    # Let's ignore other message types for now
                    continue
        finally:
            connection.close()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            connection = create_connection(config=config)
        except Exception as e:
            logger.error(f'Failed to create connection. Error: {e}')
            return AirbyteConnectionStatus(status=Status.FAILED, message=f'Could not create connection: {repr(e)}')
        try:
            channel = connection.channel()
            if channel.is_open:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            return AirbyteConnectionStatus(status=Status.FAILED, message='Could not open channel')
        except Exception as e:
            logger.error(f'Failed to open RabbitMQ channel. Error: {e}')
            return AirbyteConnectionStatus(status=Status.FAILED, message=f'An exception occurred: {repr(e)}')
        finally:
            connection.close()
