#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
    Type,
)
from destination_dewey.client import DeweyClient
from destination_dewey.config import DeweyConfig
from destination_dewey.writer import DeweyWriter


class DestinationDewey(Destination):
    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        config_model = DeweyConfig.parse_obj(config)
        client = DeweyClient(config_model)
        writer = DeweyWriter(
            client=client,
            catalog=configured_catalog,
            stream_collections=config_model.stream_collections,
            auto_create_collections=config_model.auto_create_collections,
            text_fields=config_model.text_fields,
            title_field=config_model.title_field,
            metadata_fields=config_model.metadata_fields,
            flush_interval=config_model.flush_interval,
            parallelize=config_model.parallelize,
        )

        writer.resolve_collections()
        writer.delete_streams_to_overwrite()

        for message in input_messages:
            if message.type == Type.STATE:
                writer.flush()
                yield message
            elif message.type == Type.RECORD:
                writer.queue(message.record)
            else:
                continue
        writer.flush()

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            config_model = DeweyConfig.parse_obj(config)
            client = DeweyClient(config_model)
            error = client.check()
            if error:
                return AirbyteConnectionStatus(status=Status.FAILED, message=error)

            for stream_id, collection_id in config_model.stream_collections.items():
                col = client.get_collection(collection_id)
                if col is None:
                    return AirbyteConnectionStatus(
                        status=Status.FAILED,
                        message=f"Collection `{collection_id}` for stream `{stream_id}` not found in Dewey.",
                    )
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/dewey",
            supportsIncremental=True,
            supported_destination_sync_modes=[
                DestinationSyncMode.overwrite,
                DestinationSyncMode.append,
                DestinationSyncMode.append_dedup,
            ],
            connectionSpecification=DeweyConfig.schema(),
        )
