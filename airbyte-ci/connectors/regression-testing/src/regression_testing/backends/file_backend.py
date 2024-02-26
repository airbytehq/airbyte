import os
from collections import defaultdict
from typing import Any, Dict, Generator, Tuple

from airbyte_protocol.models import AirbyteMessage
from airbyte_protocol.models import Type as AirbyteMessageType

from .base_backend import BaseBackend


class FileBackend(BaseBackend):
    RELATIVE_RECORDS_PATH = "records.json"
    RELATIVE_STATES_PATH = "states.json"

    def __init__(self, output_directory: str):
        self._output_directory = output_directory

    async def write(self, messages: Generator[AirbyteMessage, Any, None]):
        streams_to_records, streams_to_states = self._get_per_stream_records_and_states(messages)
        for stream in streams_to_states | streams_to_records:
            os.makedirs(f"{self._output_directory}/{stream}", exist_ok=True)

        for stream, records in streams_to_records.items():
            with open(f"{self._output_directory}/{stream}/{self.RELATIVE_RECORDS_PATH}", "w") as records_file:
                # TODO: sort & filter out things like timestamp
                for record in records:
                    records_file.write(f"{record.json()}\n")

        for stream, states in streams_to_states.items():
            with open(f"{self._output_directory}/{stream}/{self.RELATIVE_STATES_PATH}", "w") as states_file:
                for state in states:
                    states_file.write(f"{state.json()}\n")

    def _get_per_stream_records_and_states(self, messages: Generator[AirbyteMessage, Any, None]) -> Tuple[Dict, Dict]:
        streams_to_records = defaultdict(list)
        streams_to_states = defaultdict(list)
        for message in messages:
            if message.type == AirbyteMessageType.RECORD:
                streams_to_records[message.record.stream].append(message.record)
            elif message.type == AirbyteMessageType.STATE:
                stream_name = message.state.stream.stream_descriptor.name
                stream_namespace = message.state.stream.stream_descriptor.namespace
                key = f"{stream_name}_{stream_namespace}" if stream_namespace else stream_name
                streams_to_states[key].append(message.state)

        return streams_to_records, streams_to_states

    async def read(self):
        raise NotImplementedError

    async def compare(self):
        raise NotImplementedError
