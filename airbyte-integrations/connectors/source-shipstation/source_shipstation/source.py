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
                        "type": "list",
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
                    print(data, "----")
                    if isinstance(data, list):
                        
                        for record in data:
                            print(record, type(record),  "---------")
                            emitted_at = int(time.mktime(datetime.datetime.now().timetuple()))
                            yield AirbyteRecordMessage(stream=stream_name, data=record, emitted_at=emitted_at)
                    yield AirbyteRecordMessage(stream=stream_name, data={"msg":"not list"}, emitted_at=emitted_at)
        except Exception as e:
            # Handle any exceptions that occurred during the read process
            logger.error(f"Error during read: {str(e)}")