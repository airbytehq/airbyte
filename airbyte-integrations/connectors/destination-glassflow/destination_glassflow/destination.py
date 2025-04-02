#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from logging import Logger, getLogger
from typing import Any, Iterable, Mapping

from glassflow import PipelineDataSink, PipelineDataSource, errors

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type


logger = getLogger("airbyte")


def create_source_connection(config: Mapping[str, Any]) -> PipelineDataSource:
    pipeline_id = config.get("pipeline_id")
    pipeline_access_token = config.get("pipeline_access_token")

    return PipelineDataSource(pipeline_id=pipeline_id, pipeline_access_token=pipeline_access_token)


def create_sink_connection(config: Mapping[str, Any]) -> PipelineDataSink:
    pipeline_id = config.get("pipeline_id")
    pipeline_access_token = config.get("pipeline_access_token")

    return PipelineDataSink(pipeline_id=pipeline_id, pipeline_access_token=pipeline_access_token)


class DestinationGlassflow(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
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
        streams = {s.stream.name for s in configured_catalog.streams}
        connection = create_source_connection(config)

        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message means all records that came before it
                # have already been published.
                yield message
            elif message.type == Type.RECORD:
                record = message.record
                if record.stream not in streams:
                    # Message contains record from a stream that is not in the catalog. Skip it!
                    logger.debug(f"Stream {record.stream} was not present in configured streams, skipping")
                    continue
                connection.publish(
                    {
                        "stream": record.stream,
                        "namespace": record.namespace,
                        "emitted_at": record.emitted_at,
                        "data": record.data,
                    }
                )
            else:
                logger.info(f"Message type {message.type} not supported, skipping")
                continue

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
        try:
            connection = create_source_connection(config)
            try:
                connection.validate_credentials()
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            except errors.PipelineAccessTokenInvalidError:
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"The pipeline access token is not valid")
        except Exception as e:
            logger.error(f"Failed to create connection. Error: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
