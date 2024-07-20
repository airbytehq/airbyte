#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging

from typing import Any, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status
from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.config.validation import ConfigValidator
from destination_palantir_foundry.foundry_api.compass import CompassFactory
from destination_palantir_foundry.foundry_api.foundry_auth import ConfidentialClientAuthFactory
from destination_palantir_foundry.writer.writer_factory import WriterFactory
from airbyte_cdk.models.airbyte_protocol import Type

logger = logging.getLogger("airbyte")


class DestinationPalantirFoundry(Destination):
    def __init__(self, foundry_writer_factory: WriterFactory) -> None:
        super().__init__()
        self.foundry_writer_factory = foundry_writer_factory

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
        foundry_config = FoundryConfig.from_raw(config)

        foundry_writer = self.foundry_writer_factory.create()

        for stream in configured_catalog.streams:
            foundry_writer.ensure_registered(
                stream.stream.namespace, stream.stream.name)

        for message in input_messages:
            if message.type == Type.RECORD:
                record = message.record
                foundry_writer.add_row(
                    record.namespace, record.stream, record.data)

            elif message.type == Type.STATE:
                stream_descriptor = message.state.stream.stream_descriptor
                foundry_writer.ensure_flushed(
                    stream_descriptor.namespace, stream_descriptor.name)
                logger.info(
                    f"Ensured '[{stream_descriptor.namespace}] {stream_descriptor.name}' was flushed.")
                yield message

            else:
                logger.info(
                    f"Received unsupported message type {message.type}")
                continue

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
            foundry_config = FoundryConfig.from_raw(config)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Invalid config spec format.")

        config_validator = ConfigValidator(
            logger, CompassFactory(), ConfidentialClientAuthFactory())
        config_error = config_validator.get_config_errors(foundry_config)
        if config_error is not None:
            return AirbyteConnectionStatus(status=Status.FAILED, message=config_error)

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)
