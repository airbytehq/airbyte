#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from logging import Logger, getLogger
from typing import Any, Dict, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_meilisearch.writer import MeiliWriter
from meilisearch import Client

logger = getLogger("airbyte")


def get_client(config: Mapping[str, Any]) -> Client:
    host = config.get("host")
    api_key = config.get("api_key")
    return Client(host, api_key)


class DestinationMeilisearch(Destination):
    primary_key = "_ab_pk"

    def _flush_streams(self, streams: Dict[str, MeiliWriter]) -> Iterable[AirbyteMessage]:
        for stream in streams:
            streams[stream].flush()

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        client = get_client(config=config)
        # Creating Meilisearch writers
        writers = {s.stream.name: MeiliWriter(client, s.stream.name, self.primary_key) for s in configured_catalog.streams}

        for configured_stream in configured_catalog.streams:
            stream_name = configured_stream.stream.name
            # Deleting index in Meilisearch if sync mode is overwite
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                logger.debug(f"Deleting index: {stream_name}.")
                client.delete_index(stream_name)
            # Creating index in Meilisearch
            client.create_index(stream_name, {"primaryKey": self.primary_key})
            logger.debug(f"Creating index: {stream_name}.")

        for message in input_messages:
            if message.type == Type.STATE:
                yield message
            elif message.type == Type.RECORD:
                data = message.record.data
                stream = message.record.stream
                # Skip unselected streams
                if stream not in writers:
                    logger.debug(f"Stream {stream} was not present in configured streams, skipping")
                    continue
                writers[stream].queue_write_operation(data)
            else:
                logger.info(f"Unhandled message type {message.type}: {message}")

        # Flush any leftover messages
        self._flush_streams(writers)

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            client = get_client(config=config)

            client.create_index("_airbyte", {"primaryKey": "id"})

            client.index("_airbyte").add_documents(
                [
                    {
                        "id": 287947,
                        "title": "Shazam",
                        "overview": "A boy is given the ability",
                    }
                ]
            )

            client.delete_index("_airbyte")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Check connection failed. Error: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
