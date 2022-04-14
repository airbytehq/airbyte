#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping
from google.auth.exceptions import RefreshError
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status
from .auth import GoogleSpreadsheetsAuth
from .helpers import connection_test_write


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
            client = GoogleSpreadsheetsAuth.authenticate(config)
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
        
        pass
