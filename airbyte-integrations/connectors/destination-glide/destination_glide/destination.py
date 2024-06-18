#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    Status,
    DestinationSyncMode,
    Type
)
from collections import defaultdict
import datetime
import json
import logging
from typing import Any, Iterable, Mapping
import uuid


# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler
# TODO REMOVE?
handler = logging.FileHandler('destination-glide.log')
handler.setLevel(logging.DEBUG)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)

class DestinationGlide(Destination):
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

        stream_names = {s.stream.name for s in configured_catalog.streams}
        for configured_stream in configured_catalog.streams:
            if configured_stream.destination_sync_mode != DestinationSyncMode.overwrite:
                raise Exception(f"Only destination sync mode overwrite it supported, but received '{configured_stream.destination_sync_mode}'.")
            # TODO: create a new GBT to prepare for dumping the data into it
            table_name = f"_bgt_{configured_stream.stream.name}"

            # stream the records into the GBT:
            buffer = defaultdict(list)
            for message in input_messages:
                if message.type == Type.RECORD:
                    data = message.record.data
                    stream = message.record.stream
                    if stream not in stream_names:
                        logger.debug(f"Stream {stream} was not present in configured streams, skipping")
                        continue
                    
                    # TODO: Check the columns match the columns that we saw in configured_catalog per https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#destination

                    # add to buffer
                    record_id = str(uuid.uuid4())
                    buffer[stream].append((record_id, datetime.datetime.now().isoformat(), json.dumps(data)))
                    logger.debug(f"Added record to buffer: {buffer[stream][len(buffer[stream])-1]}")

                if message.type == Type.STATE:
                    # TODO: This is a queue from the source that we should save the buffer of records from message.type == Type.RECORD messages. See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#state--the-whole-sync
                    logger.warning(f"TODO: DUMP buffer with {len(buffer.items())} records into the GBT!")
                    yield message
        pass

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
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
            # TODO

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
