#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    Status,
)
from airbyte_cdk.sources import Source


class SourceDebug(Source):
    def _load_messages(self, config: json) -> Generator[AirbyteMessage, None, None]:
        # each message is a jsonl string (each line should be parsed as a json object and then converted to an AirbyteMessage)
        for message in config["messages"]:
            for message_line in message["text"].split("\n"):
                if message_line.strip() != "":
                    yield AirbyteMessage.parse_obj(json.loads(message_line))
    
    def _load_catalog(self, config: json) -> AirbyteCatalog:
        return AirbyteCatalog.parse_obj(json.loads(config["catalog"]))

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:
            self._load_messages(config)
            self._load_catalog(config)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        return self._load_catalog(config)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        exit_code = config["exit_code"]
        yield from self._load_messages(config)
        # exit with the provided exit code
        exit(exit_code)
