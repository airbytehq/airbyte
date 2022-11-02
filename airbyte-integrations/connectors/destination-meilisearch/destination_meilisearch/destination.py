#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from logging import Logger
from typing import Any, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_meilisearch.writer import MeiliWriter
from meilisearch import Client


def get_client(config: Mapping[str, Any]) -> Client:
    host = config.get("host")
    api_key = config.get("api_key")
    return Client(host, api_key)


class DestinationMeilisearch(Destination):
    primary_key = "_ab_pk"

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        client = get_client(config=config)

        for configured_stream in configured_catalog.streams:
            steam_name = configured_stream.stream.name
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                client.delete_index(steam_name)
            client.create_index(steam_name, {"primaryKey": self.primary_key})

            writer = MeiliWriter(client, steam_name, self.primary_key)
            for message in input_messages:
                if message.type == Type.STATE:
                    writer.flush()
                    yield message
                elif message.type == Type.RECORD:
                    writer.queue_write_operation(message.record.data)
                else:
                    continue
            writer.flush()

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            client = get_client(config=config)

            create_index_job = client.create_index("_airbyte", {"primaryKey": "id"})
            client.wait_for_task(create_index_job["taskUid"])

            add_documents_job = client.index("_airbyte").add_documents(
                [
                    {
                        "id": 287947,
                        "title": "Shazam",
                        "overview": "A boy is given the ability",
                    }
                ]
            )
            client.wait_for_task(add_documents_job.task_uid)

            client.index("_airbyte").search("Shazam")
            client.delete_index("_airbyte")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Check connection failed. Error: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
