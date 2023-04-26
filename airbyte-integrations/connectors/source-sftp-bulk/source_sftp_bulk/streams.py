#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin, Stream

from .client import SFTPClient


class FTPStream(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "last_modified"

    def __init__(self, config: Mapping[str, Any], start_date: datetime, connection: SFTPClient, json_schema: Mapping[str, Any], **kwargs):
        super(Stream, self).__init__(**kwargs)

        self.config = config
        self.start_date = start_date
        self.connection = connection

        self._cursor_value: float = None
        self._name = config["stream_name"]
        self._only_most_recent_file: bool = config.get("file_most_recent", False)
        self._json_schema = json_schema

        if self._only_most_recent_file:
            self.cursor_field = None

    @property
    def name(self) -> str:
        """Source name"""
        return self._name

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.isoformat()}

        return {self.cursor_field: self.start_date.isoformat()}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.fromisoformat(value[self.cursor_field])

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if stream_state and sync_mode == SyncMode.incremental:
            self._cursor_value = datetime.fromisoformat(stream_state[self.cursor_field])

        if not stream_state and sync_mode == SyncMode.incremental:
            self._cursor_value = self.start_date

        files = self.connection.get_files(
            self.config.get("folder_path"),
            self.config.get("file_pattern"),
            modified_since=self._cursor_value,
            most_recent_only=self._only_most_recent_file,
        )

        for cursor, records in self.connection.fetch_files(
            files=files, file_type=self.config["file_type"], separator=self.config.get("separator")
        ):
            if cursor and sync_mode == SyncMode.incremental:
                if self._cursor_value and cursor > self._cursor_value:
                    self._cursor_value = cursor

            yield from records
