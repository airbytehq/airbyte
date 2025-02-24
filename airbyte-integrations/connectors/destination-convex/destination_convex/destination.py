#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from logging import Logger
from typing import Any, Iterable, List, Mapping, Optional, cast

import requests

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    Type,
)
from destination_convex.client import ConvexClient
from destination_convex.config import ConvexConfig
from destination_convex.writer import ConvexWriter


class DestinationConvex(Destination):
    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
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
        config = cast(ConvexConfig, config)
        writer = ConvexWriter(ConvexClient(config, self.table_metadata(configured_catalog.streams)))

        # Setup: Clear tables if in overwrite mode; add indexes if in append_dedup mode.
        streams_to_delete = []
        indexes_to_add = {}
        for configured_stream in configured_catalog.streams:
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                streams_to_delete.append(configured_stream.stream.name)
            elif configured_stream.destination_sync_mode == DestinationSyncMode.append_dedup and configured_stream.primary_key:
                indexes_to_add[configured_stream.stream.name] = configured_stream.primary_key
        if len(streams_to_delete) != 0:
            writer.delete_tables(streams_to_delete)
        if len(indexes_to_add) != 0:
            writer.add_indexes(indexes_to_add)

        # Process records
        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                writer.flush()
                yield message
            elif message.type == Type.RECORD and message.record is not None:
                table_name = self.table_name_for_stream(
                    message.record.namespace,
                    message.record.stream,
                )
                msg = {
                    "tableName": table_name,
                    "data": message.record.data,
                }
                writer.queue_write_operation(msg)
            else:
                # ignore other message types for now
                continue

        # Make sure to flush any records still in the queue
        writer.flush()

    def table_name_for_stream(self, namespace: Optional[str], stream_name: str) -> str:
        if namespace is not None:
            return f"{namespace}_{stream_name}"
        return stream_name

    def table_metadata(
        self,
        streams: List[ConfiguredAirbyteStream],
    ) -> Mapping[str, Any]:
        table_metadata = {}
        for s in streams:
            # Only send a primary key for dedup sync
            if s.destination_sync_mode != DestinationSyncMode.append_dedup:
                s.primary_key = None
            stream = {
                "primaryKey": s.primary_key,
                "jsonSchema": s.stream.json_schema,
            }
            name = self.table_name_for_stream(
                s.stream.namespace,
                s.stream.name,
            )
            table_metadata[name] = stream
        return table_metadata

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        config = cast(ConvexConfig, config)
        deployment_url = config["deployment_url"]
        access_key = config["access_key"]
        url = f"{deployment_url}/version"
        headers = {"Authorization": f"Convex {access_key}"}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        else:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(resp)}")
