#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import random
import string
from typing import Any, Iterable, Mapping
import logging

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type

from .client import Client
from .utils import get_schema_from_catalog


class DestinationWeaviate(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
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
        client = Client(config, get_schema_from_catalog(configured_catalog))

        for configured_stream in configured_catalog.streams:

            # we delete first, and no longer re-create our deleted stream
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                client.delete_stream_entries(configured_stream.stream)

            # check to see if our stream exists in our weaviate schema instance
            # if not, we do not rely on auto schema to create it if we happen to have null / none entries
            # see issue #24378
            existing_weaviate_schema = client.get_current_weaviate_schema(configured_stream.stream.name)
            if not existing_weaviate_schema:
                logging.info(f"Generating new weaviate class schema from configured catalogue stream {configured_stream.stream.name}")
                client.create_class_from_stream(configured_stream.stream)


        return client.batch_buffered_write(input_messages)

        # Note: the code below bufferds writes serially
        # You can enable this if you do not want the new multirheaded buffered writes in the method above

        # for message in input_messages:
        #     if message.type == Type.STATE:
        #         # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
        #         # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
        #         client.flush()
        #         yield message
        #     elif message.type == Type.RECORD:
        #         record = message.record
        #         client.buffered_write_operation(record.stream, record.data)
        #     else:
        #         # ignore other message types for now
        #         continue

        # # Make sure to flush any records still in the queue
        # client.flush()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            client = Client.get_weaviate_client(config)
            ready = client.is_ready()
            if not ready:
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"Weaviate server {config.get('url')} not ready")

            class_name = "".join(random.choices(string.ascii_uppercase, k=10))
            client.schema.create_class({"class": class_name})
            client.schema.delete_class(class_name)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
