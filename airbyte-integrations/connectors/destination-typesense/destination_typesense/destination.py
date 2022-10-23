#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status
from typesense import Client

def get_client(config: Mapping[str, Any]) -> Client:
    api_key = config.get("api_key")
    host = config.get("host")
    port = config.get("port")
    protocol = config.get("protocol")

    client = typesense.Client({
    'api_key': api_key,
    'nodes': [{
        'host': host,
        'port': port,
        'protocol': protocol
    }],
    'connection_timeout_seconds': 2
    })

    return client

class DestinationTypesense(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        """
        TODO
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """

        pass

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            client = get_client(config=config)
            create_collection = client.collections.create({
                "name": "_airbyte",
                "fields": [{"name": "title", "type": "string"}]
            })
            client.collections['_airbyte'].documents.create({'id': '1', 'title': 'The Hunger Games'})
            client.collections['_airbyte'].documents['1'].retrieve()
            client.collections['_airbyte'].delete()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
