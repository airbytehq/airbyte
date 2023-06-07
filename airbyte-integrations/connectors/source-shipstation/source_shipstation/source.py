#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import requests
import base64
import datetime
import time
from typing import Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source

from airbyte_cdk.models.airbyte_protocol import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from typing import Iterable


class SourceShipstation(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            base_url = config["base_url"]
            api_key = config["api_key"]
            api_secret = config["api_secret"]

            url = f"{base_url}/users?showInactive=false"
            payload = {}
            
            response=requests.get(url, auth=(api_key,api_secret), params=payload,)

            # Check the response status code and content to determine the connection status
            if response.status_code == 200:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(status=Status.FAILED, message="Failed to connect to ShipStation API")

        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    # def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
    #     """
    #     Returns an AirbyteCatalog representing the available streams and fields in this integration.
    #     For example, given valid credentials to a Postgres database,
    #     returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

    #     :param logger: Logging object to display debug/info/error to the logs
    #         (logs will not be accessible via airbyte UI if they are not passed to this logger)
    #     :param config: Json object containing the configuration of this source, content of this json is as specified in
    #     the properties of the spec.yaml file

    #     :return: AirbyteCatalog is an object describing a list of all available streams in this source.
    #         A stream is an AirbyteStream object that includes:
    #         - its stream name (or table name in the case of Postgres)
    #         - json_schema providing the specifications of expected schema for this stream (a list of columns described
    #         by their names and types)
    #     """
    #     streams = []

    #     stream_name = "TableName"  # Example
    #     json_schema = {  # Example
    #         "$schema": "http://json-schema.org/draft-07/schema#",
    #         "type": "object",
    #         "properties": {"columnName": {"type": "string"}},
    #     }

    #     # Not Implemented

    #     streams.append(AirbyteStream(name=stream_name, json_schema=json_schema))
    #     return AirbyteCatalog(streams=streams)
    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        try:
            # Retrieve configuration values from the config
            base_url = config["base_url"]
            api_key = config["api_key"]
            api_secret = config["api_secret"]

            # Make API request to fetch the available streams from ShipStation
            url = f"{base_url}/carriers/"
            payload = {}
            response = requests.get(url, auth=(api_key, api_secret), params=payload)

            # Check if the API request was successful
            if response.status_code == 200:
                # Parse the response to get the list of available streams
                stream_data = response.json()

                streams = []
                for stream in stream_data:
                    # Create an AirbyteStream for each stream
                    stream_name = stream["name"]
                    # Define the json_schema for the stream (example schema provided)
                    json_schema = {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "properties": {"columnName": {"type": "string"}},
                    }
                    # Define the supported sync modes for the stream
                    supported_sync_modes = ["full_refresh", "incremental"]

                    # Create the AirbyteStream with all the required fields
                    airbyte_stream = AirbyteStream(
                        name=stream_name,
                        json_schema=json_schema,
                        supported_sync_modes=supported_sync_modes,
                    )
                    streams.append(airbyte_stream)

                # Create and return the AirbyteCatalog with the list of streams
                return AirbyteCatalog(streams=streams)
            else:
                return AirbyteCatalog(streams=[])

        except Exception as e:
            # Handle any exceptions that occurred during the discovery process
            logger.error(f"Error during discovery: {str(e)}")
            return AirbyteCatalog(streams=[])


    # def read(
    #     self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    # ) -> Generator[AirbyteMessage, None, None]:
    #     """
    #     Returns a generator of the AirbyteMessages generated by reading the source with the given configuration,
    #     catalog, and state.

    #     :param logger: Logging object to display debug/info/error to the logs
    #         (logs will not be accessible via airbyte UI if they are not passed to this logger)
    #     :param config: Json object containing the configuration of this source, content of this json is as specified in
    #         the properties of the spec.yaml file
    #     :param catalog: The input catalog is a ConfiguredAirbyteCatalog which is almost the same as AirbyteCatalog
    #         returned by discover(), but
    #     in addition, it's been configured in the UI! For each particular stream and field, there may have been provided
    #     with extra modifications such as: filtering streams and/or columns out, renaming some entities, etc
    #     :param state: When a Airbyte reads data from a source, it might need to keep a checkpoint cursor to resume
    #         replication in the future from that saved checkpoint.
    #         This is the object that is provided with state from previous runs and avoid replicating the entire set of
    #         data everytime.

    #     :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
    #     """
    #     stream_name = "TableName"  # Example
    #     data = {"columnName": "Hello World"}  # Example

    #     # Not Implemented

    #     yield AirbyteMessage(
    #         type=Type.RECORD,
    #         record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
    #     )

    # def read(
    #     self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteStream
    # ) -> Iterable[AirbyteMessage]:
    def read(self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]) -> Generator[AirbyteMessage, None, None]:
        try:
            # Retrieve configuration values from the config
            base_url = config["base_url"]
            api_key = config["api_key"]
            api_secret = config["api_secret"]

            for stream in catalog.streams:
                stream_name = stream.stream.name
                sync_mode = stream.sync_mode
                print(stream_name, sync_mode)
                # Make API request to fetch data from ShipStation for the specified stream
                url = f"{base_url}/{stream_name}/"
                payload = {}
                response = requests.get(url, auth=(api_key, api_secret), params=payload)
                # Check if the API request was successful
                if response.status_code == 200:
                    # Parse the response to get the data records
                    data = response.json()
                    for record in data:
                        emitted_at = int(time.mktime(datetime.datetime.now().timetuple()))
                        yield AirbyteRecordMessage(stream=stream_name, data=record, emitted_at=emitted_at)
        except Exception as e:
            # Handle any exceptions that occurred during the read process
            logger.error(f"Error during read: {str(e)}")

            # Handle incremental sync mode
            # if sync_mode == SyncMode.incremental:
                # Check for a `cursor_field` in the catalog to support pagination or incremental updates
                # if catalog.cursor_field:
                    # Implement your logic here to handle pagination or incremental updates
                    # Fetch the next page of data using the cursor field, if applicable
                    # Create AirbyteRecordMessage for each data record on the next page

                    # Example code to demonstrate the usage of pagination
                    # while has_more_pages:
                        # Make the API request for the next page using the cursor field
                        # Parse the response and create AirbyteRecordMessage for each data record
                        # Update the cursor value for the next page

                        # yield AirbyteRecordMessage(stream=stream_name, data=record)

            # Handle other sync modes and error cases
            # ...

        # except Exception as e:
        #     # Handle any exceptions that occurred during the read process
        #     logger.error(f"Error during read: {str(e)}")
