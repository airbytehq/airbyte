# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Union

from airbyte_protocol.models import AirbyteMessage  # type: ignore
from airbyte_protocol.models import Type as AirbyteMessageType
from live_tests.commons.backends.base_backend import BaseBackend


class FileBackend(BaseBackend):
    RELATIVE_CATALOGS_PATH = "catalog.jsonl"
    RELATIVE_CONNECTION_STATUS_PATH = "connection_status.jsonl"
    RELATIVE_RECORDS_PATH = "records.jsonl"
    RELATIVE_SPECS_PATH = "spec.jsonl"
    RELATIVE_STATES_PATH = "states.jsonl"
    RELATIVE_TRACES_PATH = "traces.jsonl"
    RELATIVE_LOGS_PATH = "logs.jsonl"
    RELATIVE_CONTROLS_PATH = "controls.jsonl"

    def __init__(self, output_directory: Path):
        self._output_directory = output_directory

    def write(self, airbyte_messages: Iterable[AirbyteMessage]):
        messages_by_type = self._get_messages_by_type(airbyte_messages)

        if messages_by_type["catalog"]:
            with open(f"{self._output_directory}/{self.RELATIVE_CATALOGS_PATH}", "w") as catalogs_file:
                for catalog in messages_by_type["catalog"]:
                    catalogs_file.write(f"{catalog.json()}\n")

        if messages_by_type["connection_status"]:
            with open(f"{self._output_directory}/{self.RELATIVE_CONNECTION_STATUS_PATH}", "w") as statuses_file:
                for status in messages_by_type["connection_status"]:
                    statuses_file.write(f"{status.json()}\n")

        assert isinstance(messages_by_type["records"], dict)
        for stream, records in messages_by_type["records"].items():
            with open(f"{self._output_directory}/{stream}_{self.RELATIVE_RECORDS_PATH}", "w") as records_file:
                # TODO: sort & filter out things like timestamp
                for record in records:
                    records_file.write(f"{record.json()}\n")

        if messages_by_type["spec"]:
            with open(f"{self._output_directory}/{self.RELATIVE_SPECS_PATH}", "w") as specs_file:
                for spec in messages_by_type["spec"]:
                    specs_file.write(f"{spec.json()}\n")

        if messages_by_type["traces"]:
            with open(f"{self._output_directory}/{self.RELATIVE_TRACES_PATH}", "w") as trace_file:
                for trace in messages_by_type["traces"]:
                    trace_file.write(f"{trace.json()}\n")

        if messages_by_type["logs"]:
            with open(f"{self._output_directory}/{self.RELATIVE_LOGS_PATH}", "w") as log_file:
                for log in messages_by_type["logs"]:
                    log_file.write(f"{log.json()}\n")

        if messages_by_type["controls"]:
            with open(f"{self._output_directory}/{self.RELATIVE_CONTROLS_PATH}", "w") as control_file:
                for control in messages_by_type["controls"]:
                    control_file.write(f"{control.json()}\n")

        assert isinstance(messages_by_type["states"], dict)
        for stream, states in messages_by_type["states"].items():
            with open(f"{self._output_directory}/{stream}_{self.RELATIVE_STATES_PATH}", "w") as states_file:
                for state in states:
                    states_file.write(f"{state.json()}\n")

    @staticmethod
    def _get_messages_by_type(messages: Iterable[AirbyteMessage]) -> Dict[str, Union[List, Dict]]:
        messages_by_type: Dict[str, Union[List, Dict]] = {
            "catalog": [],
            "connection_status": [],
            "records": defaultdict(list),
            "spec": [],
            "states": defaultdict(list),
            "traces": [],
            "logs": [],
            "controls": [],
        }

        for message in messages:
            if not isinstance(message, AirbyteMessage):
                continue

            if message.type == AirbyteMessageType.CATALOG:
                assert isinstance(messages_by_type["catalog"], list)
                messages_by_type["catalog"].append(message.catalog)

            elif message.type == AirbyteMessageType.CONNECTION_STATUS:
                assert isinstance(messages_by_type["connection_status"], list)
                messages_by_type["connection_status"].append(message.connectionStatus)

            elif message.type == AirbyteMessageType.RECORD:
                assert isinstance(messages_by_type["records"], dict)
                messages_by_type["records"][message.record.stream].append(message.record)

            elif message.type == AirbyteMessageType.SPEC:
                assert isinstance(messages_by_type["spec"], list)
                messages_by_type["spec"].append(message.spec)

            elif message.type == AirbyteMessageType.STATE:
                if message.state.stream and message.state.stream.stream_descriptor:
                    stream_name = message.state.stream.stream_descriptor.name
                    stream_namespace = message.state.stream.stream_descriptor.namespace
                    key = f"{stream_name}_{stream_namespace}" if stream_namespace else stream_name
                else:
                    key = "_global_states"
                assert isinstance(messages_by_type["states"], dict)
                messages_by_type["states"][key].append(message.state)
            elif message.type == AirbyteMessageType.TRACE:
                assert isinstance(messages_by_type["traces"], list)
                messages_by_type["traces"].append(message.trace)
            elif message.type == AirbyteMessageType.LOG:
                assert isinstance(messages_by_type["logs"], list)
                messages_by_type["logs"].append(message.log)
            elif message.type == AirbyteMessageType.CONTROL:
                assert isinstance(messages_by_type["controls"], list)
                messages_by_type["controls"].append(message.control)
        return messages_by_type
