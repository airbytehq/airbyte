#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping

from google.auth.exceptions import RefreshError

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type

from .client import GoogleSheetsClient
from .helpers import ConnectionTest, get_spreadsheet_id, get_streams_from_catalog
from .spreadsheet import GoogleSheets
from .writer import GoogleSheetsWriter


class DestinationGoogleSheets(Destination):
    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Connection check method for Google Spreadsheets.
        Info:
            Checks whether target spreadsheet_id is available using provided credentials.
        Returns:
            :: Status.SUCCEEDED - if creadentials are valid, token is refreshed, target spreadsheet is available.
            :: Status.FAILED - if could not obtain new token, target spreadsheet is not available or other exception occured (with message).
        """
        spreadsheet_id = get_spreadsheet_id(config["spreadsheet_id"])
        try:
            client = GoogleSheetsClient(config).authorize()
            spreadsheet = GoogleSheets(client, spreadsheet_id)
            check_result = ConnectionTest(spreadsheet).perform_connection_test()
            if check_result:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except RefreshError as token_err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{token_err}")
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages, config, and catalog to write data to the destination.
        """
        spreadsheet_id = get_spreadsheet_id(config["spreadsheet_id"])

        client = GoogleSheetsClient(config).authorize()
        spreadsheet = GoogleSheets(client, spreadsheet_id)
        writer = GoogleSheetsWriter(spreadsheet)

        # get streams from catalog up to the limit
        configured_streams = get_streams_from_catalog(configured_catalog)
        # getting stream names explicitly
        configured_stream_names = [stream.stream.name for stream in configured_streams]

        for configured_stream in configured_streams:
            writer.init_buffer_stream(configured_stream)
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                writer.delete_stream_entries(configured_stream.stream.name)

        for message in input_messages:
            if message.type == Type.RECORD:
                record = message.record
                # process messages for available streams only
                if record.stream in configured_stream_names:
                    writer.add_to_buffer(record.stream, record.data)
                    writer.queue_write_operation(record.stream)
            elif message.type == Type.STATE:
                # yielding a state message indicates that all preceding records have been persisted to the destination
                writer.write_whats_left()
                yield message
            else:
                continue

        # if there are any records left in buffer
        writer.write_whats_left()

        # deduplicating records for `append_dedup` sync-mode
        for configured_stream in configured_streams:
            if configured_stream.destination_sync_mode == DestinationSyncMode.append_dedup:
                writer.deduplicate_records(configured_stream)
