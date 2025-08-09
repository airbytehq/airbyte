#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
from datetime import datetime
from logging import getLogger
from typing import Any, Iterable, Mapping
from uuid import uuid4

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_databend.client import DatabendClient

from .writer import create_databend_wirter


logger = getLogger("airbyte")


class DestinationDatabend(Destination):
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
        streams = {s.stream.name for s in configured_catalog.streams}
        client = DatabendClient(**config)

        writer = create_databend_wirter(client, logger)

        for configured_stream in configured_catalog.streams:
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                writer.delete_table(configured_stream.stream.name)
                logger.info(f"Stream {configured_stream.stream.name} is wiped.")
            writer.create_raw_table(configured_stream.stream.name)

        for message in input_messages:
            if message.type == Type.STATE:
                yield message
            elif message.type == Type.RECORD:
                data = message.record.data
                stream = message.record.stream
                # Skip unselected streams
                if stream not in streams:
                    logger.debug(f"Stream {stream} was not present in configured streams, skipping")
                    continue
                writer.queue_write_data(stream, str(uuid4()), datetime.now(), json.dumps(data))

        # Flush any leftover messages
        writer.flush()

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
            client = DatabendClient(**config)
            cursor = client.open()
            cursor.execute("DROP TABLE IF EXISTS test")
            cursor.execute("CREATE TABLE if not exists test (x Int32,y VARCHAR)")
            cursor.execute("INSERT INTO test (x,y) VALUES (%,%)", [1, "yy", 2, "xx"])
            cursor.execute("DROP TABLE IF EXISTS test")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
