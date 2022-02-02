#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys
import json
import time
from datetime import datetime
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
catalog = {
    "streams": [
        {
            "stream": {
                "name": "test",
                "json_schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        }
                    }
                },
                "supported_sync_modes": [
                    "full_refresh"
                ]
            },
            "sync_mode": "full_refresh",
            "destination_sync_mode": "overwrite"
        }
    ]
}


class SourceTestConnector(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            # Not Implemented

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        self.setConfig(config)

        streams = []

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"id": {"type": "string", "index": {"type": "number"}}},
        }
        for i in range(config["resourcesNumber"]):
            streams.append(AirbyteStream(
                name="test_resource_" + str(i), json_schema=json_schema))
        return AirbyteCatalog(streams=streams)

    def read_catalog(self, catalog_path: str) -> ConfiguredAirbyteCatalog:
        ConfiguredAirbyteCatalog.parse_obj(catalog)

    def setConfig(self, config: json):
        readConfig = config.get("read")
        resourcesNumber = readConfig.get("resourcesNumber")
        recordsPerResource = readConfig.get("recordsPerResource")
        throwError = readConfig.get("throwError")
        extractRate = readConfig.get("extractRate")
        initDelay = readConfig.get("initDelay")
        if(resourcesNumber == None):
            readConfig["resourcesNumber"] = 3
        if(recordsPerResource == None):
            readConfig["recordsPerResource"] = 5000
        if(throwError == None):
            readConfig["throwError"] = False
        if(extractRate == None):
            readConfig["extractRate"] = 100
        if(initDelay == None):
            readConfig["initDelay"] = 0

    def getRecord(self, i: int, y: int) -> dict:
        stream_name = "test_resource_" + str(i)
        data = {"id": stream_name +
                "_test_record"+str(y), "index": y}
        f = {}
        f["stream_name"] = stream_name
        f["data"] = data
        return f

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        self.setConfig(config)
        resourcesNumber = config["read"]["resourcesNumber"]
        recordsPerResource = config["read"]["recordsPerResource"]
        throwError = config["read"]["throwError"]
        extractRate = config["read"]["extractRate"]
        initDelay = config["read"]["initDelay"]
        time.sleep(initDelay)
        for i in range(resourcesNumber):
            for y in range(recordsPerResource):
                if ((y % extractRate == 0)):
                    time.sleep(1)
                # throw error after the half data in the first resource
                if((round(recordsPerResource/2) == y) & throwError == True):
                    raise Exception("Expected Error")
                record = self.getRecord(i, y)
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=record["stream_name"], data=record["data"], emitted_at=int(
                        datetime.now().timestamp()) * 1000),
                )
