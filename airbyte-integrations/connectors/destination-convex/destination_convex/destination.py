#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Iterable

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_convex.client import ConvexClient
from destination_convex.config import ConvexConfig
from destination_convex.writer import ConvexWriter


class DestinationConvex(Destination):
    def write(
        self, config: ConvexConfig, configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
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

        writer = ConvexWriter(ConvexClient(config))
        # TODO put the stream metadata in the writer on initialization
        streams_to_delete = []
        indexes_to_add = {}
        for configured_stream in configured_catalog.streams:
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                streams_to_delete.append(configured_stream.stream.name)
            elif configured_stream.destination_sync_mode == DestinationSyncMode.append_dedup:
                indexes_to_add[configured_stream.stream.name] = configured_stream.primary_key
        if len(streams_to_delete) != 0:
            writer.delete_stream_entries(streams_to_delete)
        if len(indexes_to_add) != 0:
            writer.add_indexes(indexes_to_add)

        streams = {}
        for s in configured_catalog.streams:
            if s.cursor_field is None:
                cursor = []
            else:
                cursor = s.cursor_field
            if s.primary_key is None:
                primary_key = [[]]
            else:
                primary_key = s.primary_key
            stream = {
                "destinationSyncMode": str(s.destination_sync_mode.name),
                "cursor": cursor,  # need some logic to combine here
                "primaryKey": primary_key,
                "jsonSchema": str(s.stream.json_schema),  # FIXME
            }
            streams[s.stream.name] = stream
        writer.stream_metadata = streams

        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                writer.flush()
                yield message
            elif message.type == Type.RECORD and message.record is not None:
                msg = message.record.dict()
                writer.queue_write_operation(msg)
            else:
                # ignore other message types for now
                continue

        # Make sure to flush any records still in the queue
        writer.flush()

    def check(self, logger: AirbyteLogger, config: ConvexConfig) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        deployment_url = config["deployment_url"]
        access_key = config["access_key"]
        url = f"{deployment_url}/version"
        headers = {"Authorization": f"Convex {access_key}"}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        else:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(resp)}")
