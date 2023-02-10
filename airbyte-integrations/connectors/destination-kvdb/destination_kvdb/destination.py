#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import time
import traceback
import uuid
from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_kvdb.client import KvDbClient
from destination_kvdb.writer import KvDbWriter


class DestinationKvdb(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        """
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.
        """
        writer = KvDbWriter(KvDbClient(**config))

        for configured_stream in configured_catalog.streams:
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                writer.delete_stream_entries(configured_stream.stream.name)

        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                writer.flush()
                yield message
            elif message.type == Type.RECORD:
                record = message.record
                writer.queue_write_operation(
                    record.stream, record.data, time.time_ns() / 1_000_000
                )  # convert from nanoseconds to milliseconds
            else:
                # ignore other message types for now
                continue

        # Make sure to flush any records still in the queue
        writer.flush()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.
        """
        try:
            # Verify write access by attempting to write and then delete to a random key
            client = KvDbClient(**config)
            random_key = str(uuid.uuid4())
            client.write(random_key, {"value": "_airbyte_connection_check"})
            client.delete(random_key)
        except Exception as e:
            traceback.print_exc()
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"An exception occurred: {e}. \nStacktrace: \n{traceback.format_exc()}"
            )
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
