from typing import Any, Generator

from airbyte_protocol.models import AirbyteMessage
from airbyte_protocol.models import Type as AirbyteMessageType

from .base_backend import BaseBackend


class FileBackend(BaseBackend):
    RELATIVE_RECORDS_PATH = "records.json"
    RELATIVE_STATES_PATH = "states.json"

    def __init__(self, output_directory: str):
        self._output_directory = output_directory

    async def write(self, messages: Generator[AirbyteMessage, Any, None]):
        with open(f"{self._output_directory}/{self.RELATIVE_RECORDS_PATH}", "w") as records_file:
            with open(f"{self._output_directory}/{self.RELATIVE_STATES_PATH}", "w") as states_file:
                for message in messages:
                    if message.type == AirbyteMessageType.RECORD:
                        # TODO: sort & filter out things like timestamp
                        records_file.write(f"{message.record.json()}\n")
                    elif message.type == AirbyteMessageType.STATE:
                        states_file.write(f"{message.state.json()}\n")

    async def read(self):
        raise NotImplementedError

    async def compare(self):
        raise NotImplementedError
