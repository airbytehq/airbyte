from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pytz
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream

from .client import Client

PATTERN_ALL = "^.*$"
PREFIX_ROOT = "."
OLDEST_DATETIME = "2000-01-01T00:00:00.000+00:00"


class FileNotFound(Exception):
    pass


class SFTPStream(Stream):
    ab_last_modified_column = "_ab_file_last_modified"
    ab_file_path_column = "_ab_file_path"
    ab_columns = [ab_last_modified_column, ab_file_path_column]

    def __init__(
        self,
        client: Client,
        table_name: str,
        prefix: str = None,
        pattern: str = None,
        fields: Mapping[str, Any] = None,
        start_date: str = None,
    ) -> None:
        self._client = client
        self.table_name = table_name
        self.prefix = prefix or PREFIX_ROOT
        self.pattern = pattern or PATTERN_ALL
        self.fields = fields or {}
        self.start_date = self.parse_dttm(start_date or OLDEST_DATETIME)

    @classmethod
    def parse_dttm(cls, text: str) -> datetime:
        dttm = datetime.fromisoformat(text)
        if not dttm.tzinfo:
            dttm = dttm.replace(tzinfo=pytz.UTC)
        return dttm

    @classmethod
    def format_dttm(cls, dttm: datetime) -> str:
        return dttm.isoformat(timespec="seconds")

    @property
    def name(self) -> str:
        return self.table_name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        files = self._client.get_files(prefix=self.prefix, search_pattern=self.pattern, modified_since=None)
        if not files:
            raise FileNotFound(f"Could not find any files with prefix `{self.prefix}`, pattern `{self.pattern}`")
        properties = self._client.get_file_properties(files[-1]["filepath"])
        for ab_col in self.ab_columns:
            properties[ab_col] = {"type": ["string", "null"]}
        properties[self.ab_last_modified_column]["format"] = "date-time"
        properties[self.ab_last_modified_column]["airbyte_type"] = "timestamp_with_timezone"
        return {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": properties}

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        files = self._client.get_files(prefix=self.prefix, search_pattern=self.pattern, modified_since=self.start_date)
        for file in files:
            yield [file]

    def read_stream_slice(self, stream_slice: Iterable[Mapping[str, Any]], stream_state: Mapping[str, Any] = None):
        self.logger.info("Stream state: %s", stream_state)
        for file_info in stream_slice:
            # TODO: specify fields when read
            for record in self._client.read(file_path=file_info["filepath"]):
                record[self.ab_file_path_column] = file_info["filepath"]
                record[self.ab_last_modified_column] = self.format_dttm(file_info["last_modified"])
                yield record
        self.logger.debug("Completed a stream slice: %s", stream_slice)
        # Ensure always yield
        yield from []

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_slice = stream_slice or []
        yield from self.read_stream_slice(stream_slice)


class SFTPIncrementalStream(SFTPStream):
    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return None

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self.ab_last_modified_column

    @property
    def supports_incremental(self) -> bool:
        return True

    @property
    def support_sync_modes(self) -> List[SyncMode]:
        return [SyncMode.full_refresh, SyncMode.incremental]

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        lastest_record_dttm = current_state_dttm = self.start_date

        if latest_record and self.cursor_field in latest_record:
            lastest_record_dttm = self.parse_dttm(latest_record[self.cursor_field])

        if current_stream_state and self.cursor_field in current_stream_state:
            current_state_dttm = self.parse_dttm(current_stream_state[self.cursor_field])

        new_state_dttm = max(lastest_record_dttm, current_state_dttm)
        new_state = {self.cursor_field: self.format_dttm(new_state_dttm)}
        return new_state

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if sync_mode == SyncMode.full_refresh:
            yield from super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        else:
            min_modified = self.start_date
            if stream_state and self.cursor_field in stream_state:
                min_modified = max(self.start_date, self.parse_dttm(stream_state[self.cursor_field]))

            file_infos = self._client.get_files(prefix=self.prefix, search_pattern=self.pattern, modified_since=min_modified)
            prev_file_last_modified = None
            stream_slice = []

            for file_info in file_infos:
                file_last_modified = file_info["last_modified"]

                # Yield current slice when see new value of last modified time, then clear slice
                if prev_file_last_modified is not None and prev_file_last_modified != file_last_modified:
                    yield stream_slice
                    stream_slice = []

                prev_file_last_modified = file_last_modified
                # Group files with the same modified time into a slice
                stream_slice.append(file_info)

            # Yield last slice (if not empty)
            if stream_slice:
                yield stream_slice

            # Ensure yield
            yield from [None]
