#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from typing import Any

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type
from destination_deepset import util
from destination_deepset.api import APIError
from destination_deepset.models import DeepsetCloudFile, Filetypes
from destination_deepset.writer import DeepsetCloudFileWriter, WriterError

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
        writer = DeepsetCloudFileWriter.factory(config=config)

        streams: set[str] = set()
        for catalog_stream in configured_catalog.streams:
            if util.get(stream := catalog_stream.stream, "format.filetype") == Filetypes.DOCUMENT:
                streams.add(stream.name)
            else:
                logger.warning(f"Only sources that produce document file type formatted records are supported! Got {stream = !s}")

        for message in input_messages:
            match message.type:
                case Type.STATE:
                    yield message
                case Type.RECORD:
                    if (stream_name := message.record.stream) not in streams:
                        logger.debug(f"Stream {stream_name} was not present in configured streams, skipping")
                        continue

                    try:
                        file = DeepsetCloudFile.from_record(message.record)
                    except ValueError as ex:
                        yield util.get_trace_message("Failed to parse data into deepset cloud file instance.", exception=ex)
                    else:
                        yield writer.write(file=file)
                case _:
                    continue

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
        try:
            writer = DeepsetCloudFileWriter.factory(config=config)
            writer.client.health_check()
        except APIError:
            logger.exception("Failed to connect to deepset cloud API!")
        except WriterError:
            logger.exception("Failed to initialize writer due to invalid configuration!")
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        return AirbyteConnectionStatus(status=Status.FAILED, message="Failed to connect to deepset cloud!")
