import os
from collections import defaultdict
from typing import Any, Dict, Generator

from airbyte_protocol.models import AirbyteMessage
from airbyte_protocol.models import Type as AirbyteMessageType

from .base_backend import BaseBackend


class FileBackend(BaseBackend):
    RELATIVE_CATALOGS_PATH = "catalog.jsonl"
    RELATIVE_CONNECTION_STATUS_PATH = "connection_status.jsonl"
    RELATIVE_RECORDS_PATH = "records.jsonl"
    RELATIVE_SPECS_PATH = "spec.jsonl"
    RELATIVE_STATES_PATH = "states.jsonl"

    def __init__(self, output_directory: str):
        self._output_directory = output_directory

    async def write(self, messages: Generator[AirbyteMessage, Any, None]):
        messages = list(messages)
        messages_by_type = self._get_messages_by_type(messages)

        for stream in messages_by_type["records"] | messages_by_type["states"]:
            os.makedirs(f"{self._output_directory}/{stream}", exist_ok=True)

        if messages_by_type["catalog"]:
            with open(f"{self._output_directory}/{self.RELATIVE_CATALOGS_PATH}", "w") as catalogs_file:
                for catalog in messages_by_type["catalog"]:
                    catalogs_file.write(f"{catalog.json()}\n")

        if messages_by_type["connection_status"]:
            with open(f"{self._output_directory}/{self.RELATIVE_CONNECTION_STATUS_PATH}", "w") as statuses_file:
                for status in messages_by_type["connection_status"]:
                    statuses_file.write(f"{status.json()}\n")

        for stream, records in messages_by_type["records"].items():
            with open(f"{self._output_directory}/{stream}/{self.RELATIVE_RECORDS_PATH}", "w") as records_file:
                # TODO: sort & filter out things like timestamp
                for record in records:
                    records_file.write(f"{record.json()}\n")

        if messages_by_type["spec"]:
            with open(f"{self._output_directory}/{self.RELATIVE_SPECS_PATH}", "w") as specs_file:
                for spec in messages_by_type["spec"]:
                    specs_file.write(f"{spec.json()}\n")

        for stream, states in messages_by_type["states"].items():
            with open(f"{self._output_directory}/{stream}/{self.RELATIVE_STATES_PATH}", "w") as states_file:
                for state in states:
                    states_file.write(f"{state.json()}\n")

    @staticmethod
    def _get_messages_by_type(messages: Generator[AirbyteMessage, Any, None]) -> Dict[str, Dict]:
        messages_by_type = {
            "catalog": [],
            "connection_status": [],
            "records": defaultdict(list),
            "spec": [],
            "states": defaultdict(list),
        }

        for message in messages:
            if message.type == AirbyteMessageType.CATALOG:
                messages_by_type["catalog"].append(message.catalog)

            elif message.type == AirbyteMessageType.CONNECTION_STATUS:
                messages_by_type["connection_status"].append(message.connectionStatus)

            elif message.type == AirbyteMessageType.RECORD:
                messages_by_type["records"][message.record.stream].append(message.record)

            elif message.type == AirbyteMessageType.SPEC:
                messages_by_type["spec"].append(message.spec)

            elif message.type == AirbyteMessageType.STATE:
                stream_name = message.state.stream.stream_descriptor.name
                stream_namespace = message.state.stream.stream_descriptor.namespace
                key = f"{stream_name}_{stream_namespace}" if stream_namespace else stream_name
                messages_by_type["records"][key].append(message.state)

        return messages_by_type
