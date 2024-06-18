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

from .glide import GlideBigTable
import json
from .log import getLogger
import logging
import requests
from typing import Any, Iterable, Mapping
import uuid

logger = getLogger()

class DestinationGlide(Destination):
    # GlideBigTable optional for tests to inject mock
    def __init__(self, glide: GlideBigTable = None):
        if glide is None:
            glide = GlideBigTable()
        self.glide = glide

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
        # get config:
        api_host = config['api_host']
        api_path_root = config['api_path_root']
        api_key = config['api_key']
        table_id = config['table_id']
        # TODO: hardcoded for now using old api
        app_id = "Ix9CEuP6DiFugfjhSG5t"

        self.glide.init(api_host, api_key, api_path_root, app_id, table_id)

        # go through each stream and add it as needed:
        stream_names = {s.stream.name for s in configured_catalog.streams}
        for configured_stream in configured_catalog.streams:
            if configured_stream.destination_sync_mode != DestinationSyncMode.overwrite:
                raise Exception(f'Only destination sync mode overwrite it supported, but received "{configured_stream.destination_sync_mode}".') # nopep8 because https://github.com/hhatto/autopep8/issues/712

            # TODO: create a new GBT to prepare for dumping the data into it
            # NOTE: for now using an existing GBT in old API
            logger.debug("deleting all rows...")
            self.glide.delete_all()
            logger.debug("deleting all rows complete.")

            # stream the records into the GBT:
            buffer = defaultdict(list)
            logger.debug(f"buffer created.")
            for message in input_messages:
                logger.debug(f"processing message {message.type}...")
                if message.type == Type.RECORD:
                    logger.debug("buffering record...")
                    data = message.record.data
                    stream = message.record.stream
                    if stream not in stream_names:
                        logger.debug(
                            f"Stream {stream} was not present in configured streams, skipping")
                        continue

                    # TODO: Check the columns match the columns that we saw in configured_catalog per https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#destination

                    # add to buffer
                    record_id = str(uuid.uuid4())
                    buffer[stream].append(
                        (record_id, datetime.datetime.now().isoformat(), json.dumps(data)))
                    logger.debug(f"buffering record complete: {buffer[stream][len(buffer[stream])-1]}")  # nopep8 because https://github.com/hhatto/autopep8/issues/712

                elif message.type == Type.STATE:
                    # TODO: This is a queue from the source that we should save the buffer of records from message.type == Type.RECORD messages. See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#state--the-whole-sync
                    logger.debug(f"Writing '{len(buffer.items())}' buffered records to GBT...") # nopep8 because https://github.com/hhatto/autopep8/issues/712
                    self.glide.add_rows(buffer.items())
                    logger.debug(f"Writing '{len(buffer.items())}' buffered records to GBT complete.") # nopep8 because https://github.com/hhatto/autopep8/issues/712

                    yield message
                else:
                    logger.warn(f"Ignoring unknown Airbyte input message type: {message.type}")
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
