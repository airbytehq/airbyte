# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any, TextIO

from airbyte_protocol.models import AirbyteMessage  # type: ignore
from airbyte_protocol.models import Type as AirbyteMessageType
from cachetools import LRUCache, cached

from live_tests.commons.backends.base_backend import BaseBackend
from live_tests.commons.utils import sanitize_stream_name


class FileDescriptorLRUCache(LRUCache):
    def popitem(self) -> tuple[Any, Any]:
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
    CACHE = FileDescriptorLRUCache(maxsize=250)

    def __init__(self, output_directory: Path):
        self._output_directory = output_directory
        self.record_per_stream_directory = self._output_directory / "records_per_stream"
        self.record_per_stream_directory.mkdir(exist_ok=True, parents=True)
        self.record_per_stream_paths: dict[str, Path] = {}
        self.record_per_stream_paths_data_only: dict[str, Path] = {}

    @property
    def jsonl_specs_path(self) -> Path:
        return (self._output_directory / self.RELATIVE_SPECS_PATH).resolve()

    @property
    def jsonl_catalogs_path(self) -> Path:
        return (self._output_directory / self.RELATIVE_CATALOGS_PATH).resolve()

    @property
    def jsonl_connection_status_path(self) -> Path:
        return (self._output_directory / self.RELATIVE_CONNECTION_STATUS_PATH).resolve()

    @property
    def jsonl_records_path(self) -> Path:
        return (self._output_directory / self.RELATIVE_RECORDS_PATH).resolve()

    @property
    def jsonl_states_path(self) -> Path:
        return (self._output_directory / self.RELATIVE_STATES_PATH).resolve()

    @property
    def jsonl_traces_path(self) -> Path:
        return (self._output_directory / self.RELATIVE_TRACES_PATH).resolve()

    @property
    def jsonl_logs_path(self) -> Path:
        return (self._output_directory / self.RELATIVE_LOGS_PATH).resolve()

    @property
    def jsonl_controls_path(self) -> Path:
        return (self._output_directory / self.RELATIVE_CONTROLS_PATH).resolve()

    @property
    def jsonl_files(self) -> Iterable[Path]:
        return [
            self.jsonl_catalogs_path,
            self.jsonl_connection_status_path,
            self.jsonl_records_path,
            self.jsonl_specs_path,
            self.jsonl_states_path,
            self.jsonl_traces_path,
            self.jsonl_logs_path,
            self.jsonl_controls_path,
        ]

    def write(self, airbyte_messages: Iterable[AirbyteMessage]) -> None:
        """
        Write AirbyteMessages to the appropriate file.

        We use an LRU cache here to manage open file objects, in order to limit the number of concurrently open file
        descriptors. This mitigates the risk of hitting limits on the number of open file descriptors, particularly for
        connections with a high number of streams. The cache is designed to automatically close files upon eviction.
        """

        @cached(cache=self.CACHE)
        def _open_file(path: Path) -> TextIO:
            return open(path, "a")

        try:
            logging.info("Writing airbyte messages to disk")
            for _message in airbyte_messages:
                if not isinstance(_message, AirbyteMessage):
                    continue
                filepaths, messages = self._get_filepaths_and_messages(_message)
                for filepath, message in zip(filepaths, messages, strict=False):
                    _open_file(self._output_directory / filepath).write(f"{message}\n")
            logging.info("Finished writing airbyte messages to disk")
        finally:
            for f in self.CACHE.values():
                f.close()

    def _get_filepaths_and_messages(self, message: AirbyteMessage) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if message.type == AirbyteMessageType.CATALOG:
            return (self.RELATIVE_CATALOGS_PATH,), (message.catalog.json(),)

        elif message.type == AirbyteMessageType.CONNECTION_STATUS:
            return (self.RELATIVE_CONNECTION_STATUS_PATH,), (message.connectionStatus.json(),)

        elif message.type == AirbyteMessageType.RECORD:
            stream_name = message.record.stream
            stream_file_path = self.record_per_stream_directory / f"{sanitize_stream_name(stream_name)}.jsonl"
            stream_file_path_data_only = self.record_per_stream_directory / f"{sanitize_stream_name(stream_name)}_data_only.jsonl"
            self.record_per_stream_paths[stream_name] = stream_file_path
            self.record_per_stream_paths_data_only[stream_name] = stream_file_path_data_only
            return (
                self.RELATIVE_RECORDS_PATH,
                str(stream_file_path),
                str(stream_file_path_data_only),
            ), (
                message.json(sort_keys=True),
                message.json(sort_keys=True),
                json.dumps(message.record.data, sort_keys=True),
            )

        elif message.type == AirbyteMessageType.SPEC:
            return (self.RELATIVE_SPECS_PATH,), (message.spec.json(),)

        elif message.type == AirbyteMessageType.STATE:
            return (self.RELATIVE_STATES_PATH,), (message.state.json(),)

        elif message.type == AirbyteMessageType.TRACE:
            return (self.RELATIVE_TRACES_PATH,), (message.trace.json(),)

        elif message.type == AirbyteMessageType.LOG:
            return (self.RELATIVE_LOGS_PATH,), (message.log.json(),)

        elif message.type == AirbyteMessageType.CONTROL:
            return (self.RELATIVE_CONTROLS_PATH,), (message.control.json(),)

        raise NotImplementedError(f"No handling for AirbyteMessage type {message.type} has been implemented. This is unexpected.")
