#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from typing import Any

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    DestinationSyncMode,
    Status,
    Type,
)
from destination_deepset.models import DeepsetCloudFile
from destination_deepset.writer import DeepsetCloudFileWriter


logger = logging.getLogger("airbyte")


class DestinationDeepset(Destination):
    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages
        received in the input message stream. Outputting a state message means that every AirbyteRecordMessage which
        came before it has been successfully persisted to the destination. This is used to ensure fault tolerance in the
        case that a sync fails before fully completing, then the source is given the last state message output from this
        method as the starting point of the next sync.

        Args:
            config (Mapping[str, Any]): dict of JSON configuration matching the configuration declared in spec.json
            configured_catalog (ConfiguredAirbyteCatalog): The Configured Catalog describing the schema of the data
                being received and how it should be persisted in the destination
            input_messages (Iterable[AirbyteMessage]): The stream of input messages received from the source

        Returns:
            Iterable[AirbyteMessage]: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        logger.info(f"[DEEPSET] Starting write with workspace: {config.get('workspace')}")
        writer = DeepsetCloudFileWriter.factory(config)

        streams: dict[str, DestinationSyncMode] = {
            catalog_stream.stream.name: catalog_stream.destination_sync_mode
            for catalog_stream in configured_catalog.streams
        }
        logger.info(f"[DEEPSET] Configured streams: {list(streams.keys())}")

        for message in input_messages:
            if message.type == Type.STATE:
                continue
            elif message.type == Type.RECORD:
                if (destination_sync_mode := streams.get(message.record.stream)) is None:
                    logger.debug(
                        f"[DEEPSET] Stream {message.record.stream} was not present in configured streams, skipping"
                    )
                    continue

                try:
                    file = DeepsetCloudFile.from_record(message.record)
                except ValueError as ex:
                    logger.error(f"[DEEPSET] Failed to parse data into deepset cloud file instance: {ex}")
                    continue

                result = writer.write(file, destination_sync_mode=destination_sync_mode)
                if result.type == Type.TRACE:
                    logger.error(
                        f"[DEEPSET] Upload failed: {result.trace.error.message if result.trace and result.trace.error else 'unknown error'}"
                    )
        return

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Tests if the input configuration can be used to successfully connect to the destination with the needed
        permissions e.g: if a provided API token or password can be used to connect and write to the destination.

        Args:
            logger (logging.Logger): Logging object to display debug/info/error to the logs (logs will not be accessible
                via airbyte UI if they are not passed to this logger)
            config (Mapping[str, Any]): Json object containing the configuration of this destination, content of this
                json is as specified in the properties of the spec.json file

        Returns:
            AirbyteConnectionStatus: AirbyteConnectionStatus indicating a Success or Failure
        """
        logger.info(f"[DEEPSET] Checking connection to workspace: {config.get('workspace')}")
        try:
            writer = DeepsetCloudFileWriter.factory(config)
            writer.client.health_check()
            logger.info("[DEEPSET] Connection check successful")
        except Exception as ex:
            message = f"Failed to connect to deepset cloud, reason: {ex!s}"
            logger.error(f"[DEEPSET] {message}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)
