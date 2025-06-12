#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from logging import Logger, getLogger
from typing import Any, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_cumulio.client import CumulioClient
from destination_cumulio.writer import CumulioWriter


logger = getLogger("airbyte")


class DestinationCumulio(Destination):
    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received in the
        input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been successfully
        persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json. Current format:
            {
                'api_host': '<api_host_url, e.g. https://api.cumul.io>',
                'api_key': '<api_key>',
                'api_token': '<api_token>'
            }
        :param configured_catalog: schema of the data being received and how it should be persisted in the destination.
        :param input_messages: stream of input messages received from the source.

        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs.
        """
        writer = CumulioWriter(config, configured_catalog, logger)

        for configured_stream in configured_catalog.streams:
            # Cumul.io does not support removing all data from an existing dataset, and removing the dataset itself will break existing
            # dashboards built on top of it.
            # Instead, the connector will make sure to push the first batch of data as a "replace" action: this will cause all existing data
            # to be replaced with the first batch of data. All next batches will be pushed as an "append" action.
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                writer.delete_stream_entries(configured_stream.stream.name)

        for message in input_messages:
            if message.type == Type.STATE:
                # Yielding a state message indicates that all records which came before it have been written to the destination.
                # We flush all write buffers in the writer, and then output the state message itself.
                writer.flush_all()
                yield message
            elif message.type == Type.RECORD:
                record = message.record
                assert record is not None
                assert record.stream is not None
                assert record.data is not None
                writer.queue_write_operation(record.stream, record.data)
            else:
                # ignore other message types for now
                continue

        # Make sure to flush any records still in the queue
        writer.flush_all()

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Tests if the input configuration can be used to successfully connect to the destination with the needed permissions.

        This will test whether the combination of the Cumul.io API host, API key and API token is valid.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            client = CumulioClient(config, logger)
            # Verify access by hitting Cumul.io authentication endpoint
            client.test_api_token()

            # We're no longer using testing a data push as this might take some time.
            # If the API host, key, and token are valid, we can assume Data can be pushed using it.

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            # The Cumul.io Python SDK currently returns a generic error message when an issue occurs during the request,
            # or when the request return e.g. a 401 Unauthorized HTTP response code.
            # We'll assume that either the API host is incorrect, or the API key and token are no longer valid.
            if not e == "Something went wrong":
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message="An exception occurred: could it be that the API host is incorrect, or the API key and token are no longer valid?",
            )
