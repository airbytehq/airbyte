# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Iterable, TextIO, Tuple

import pydash
from airbyte_protocol.models import AirbyteMessage  # type: ignore
from airbyte_protocol.models import Type as AirbyteMessageType
from cachetools import LRUCache, cached
from live_tests.commons.backends.base_backend import BaseBackend


class FileDescriptorLRUCache(LRUCache):
    def popitem(self) -> Tuple[Any, Any]:
        filepath, fd = LRUCache.popitem(self)
        fd.close()  # type: ignore  # Close the file descriptor when it's evicted from the cache
        return filepath, fd


class FileBackend(BaseBackend):
    RELATIVE_CATALOGS_PATH = "catalog.jsonl"
    RELATIVE_CONNECTION_STATUS_PATH = "connection_status.jsonl"
    RELATIVE_RECORDS_PATH = "records.jsonl"
    RELATIVE_SPECS_PATH = "spec.jsonl"
    RELATIVE_STATES_PATH = "states.jsonl"
    RELATIVE_TRACES_PATH = "traces.jsonl"
    RELATIVE_LOGS_PATH = "logs.jsonl"
    RELATIVE_CONTROLS_PATH = "controls.jsonl"
    RECORD_PATHS_TO_POP = ["emitted_at"]
    CACHE = FileDescriptorLRUCache(maxsize=250)

    def __init__(self, output_directory: Path):
        self._output_directory = output_directory

    def write(self, airbyte_messages: Iterable[AirbyteMessage]) -> None:
        """
        Write AirbyteMessages to the appropriate file.

        Catalogs, connection status messages, specs, trace messages, logs, and control messages are all written to their
        own file (e.g. "catalog.jsonl", "spec.jsonl").

        Records and state messages are further subdivided, with one file per stream (e.g. "my_stream_records.jsonl",
        "my_stream_states.jsonl"). Streams with global state are stored in a "_global_states.jsonl" file.

        We use an LRU cache here to manage open file objects, in order to limit the number of concurrently open file
        descriptors. This mitigates the risk of hitting limits on the number of open file descriptors, particularly for
        connections with a high number of streams. The cache is designed to automatically close files upon eviction.
        """

        @cached(cache=self.CACHE)
        def _open_file(path: Path) -> TextIO:
            return open(path, "a")

        try:
            for _message in airbyte_messages:
                if not isinstance(_message, AirbyteMessage):
                    continue
                filepath, message = self._get_filepath_and_message(_message)
                _open_file(self._output_directory / filepath).write(f"{message}\n")
        finally:
            for f in self.CACHE.values():
                f.close()

    def _get_filepath_and_message(self, message: AirbyteMessage) -> Tuple[str, str]:
        if message.type == AirbyteMessageType.CATALOG:
            return self.RELATIVE_CATALOGS_PATH, message.catalog.json()

        elif message.type == AirbyteMessageType.CONNECTION_STATUS:
            return self.RELATIVE_CONNECTION_STATUS_PATH, message.connectionStatus.json()

        elif message.type == AirbyteMessageType.RECORD:
            record = json.loads(message.record.json())
            # TODO: once we have a comparator and/or database backend implemented we can remove this
            for key_path in self.RECORD_PATHS_TO_POP:
                pydash.objects.unset(record, key_path)
            return f"{message.record.stream}_{self.RELATIVE_RECORDS_PATH}", json.dumps(record)

        elif message.type == AirbyteMessageType.SPEC:
            return self.RELATIVE_SPECS_PATH, message.spec.json()

        elif message.type == AirbyteMessageType.STATE:
            if message.state.stream and message.state.stream.stream_descriptor:
                stream_name = message.state.stream.stream_descriptor.name
                stream_namespace = message.state.stream.stream_descriptor.namespace
                filepath = (
                    f"{stream_name}_{stream_namespace}_{self.RELATIVE_STATES_PATH}"
                    if stream_namespace
                    else f"{stream_name}_{self.RELATIVE_STATES_PATH}"
                )
            else:
                filepath = f"_global_{self.RELATIVE_STATES_PATH}"
            return filepath, message.state.json()

        elif message.type == AirbyteMessageType.TRACE:
            return self.RELATIVE_TRACES_PATH, message.trace.json()

        elif message.type == AirbyteMessageType.LOG:
            return self.RELATIVE_LOGS_PATH, message.log.json()

        elif message.type == AirbyteMessageType.CONTROL:
            return self.RELATIVE_CONTROLS_PATH, message.control.json()

        raise NotImplementedError(f"No handling for AirbyteMessage type {message.type} has been implemented. This is unexpected.")
