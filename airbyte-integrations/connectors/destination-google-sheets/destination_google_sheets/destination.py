#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import time
from typing import Any, Iterable, Mapping
from xml.etree.ElementPath import prepare_parent
from google.auth.exceptions import RefreshError
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, DestinationSyncMode, Type
from .client import GoogleSpreadsheetsClient
from .writer import GoogleSpreadsheetsWriter
from .helpers import connection_test_write, get_headers_from_schema


class DestinationGoogleSheets(Destination):

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Connection check method for Google Spreadsheets.
        Info: 
            Checks whether target spreadsheet_id is available using provided credentials.
        Returns:
            :: Status.SUCCEEDED - if creadentials are valid, token is refreshed, target spreadsheet is available.
            :: Status.FAILED - if could not obtain fresh token, target spreadsheet is not available or other exception occured (with message).
        """
        
        try:
            client = GoogleSpreadsheetsClient(config).client
            if connection_test_write(client, config) is True:
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
        writer = GoogleSpreadsheetsWriter(GoogleSpreadsheetsClient(config))
                
        for configured_stream in configured_catalog.streams:
            writer.buffer_stream(configured_stream)
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                writer.delete_stream_entries(configured_stream.stream.name)
                writer.set_headers(configured_stream.stream.name, get_headers_from_schema(configured_stream))

        for message in input_messages:
            if message.type == Type.STATE:
                yield message
            elif message.type == Type.RECORD:
                record = message.record
                writer.add_to_buffer(record.stream, record.data)
                writer.queue_write_operation(record.stream)
            else:
                continue
        # if there are any records left
        if writer.buffer_has_more_values():
            writer.write_whats_left()
        
        
                
        

        
