#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import itertools
import logging
from functools import cache
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.sources.file_based.exceptions import MissingSchemaError, RecordParseError, SchemaInferenceError
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import merge_schemas
from airbyte_cdk.sources.file_based.schema_validation_policies import record_passes_validation_policy
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.file_based.stream.cursor import FileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamSlice
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message


class DefaultFileBasedStream(AbstractFileBasedStream, IncrementalMixin):

    """
    The default file-based stream.
    """

    ab_last_mod_col = "_ab_source_file_last_modified"
    ab_file_name_col = "_ab_source_file_url"
    airbyte_columns = [ab_last_mod_col, ab_file_name_col]

    def __init__(self, cursor: FileBasedCursor, **kwargs):
        super().__init__(**kwargs)
        self._cursor = cursor

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._cursor.get_state()

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self._cursor.set_initial_state(value)

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.config.primary_key

    def compute_slices(self) -> Iterable[Optional[Mapping[str, Any]]]:
        # Sort files by last_modified, uri and return them grouped by last_modified
        all_files = self._list_files()
        files_to_read = self._cursor.get_files_to_sync(all_files, self.logger)
        sorted_files_to_read = sorted(files_to_read, key=lambda f: (f.last_modified, f.uri))
        slices = [{"files": list(group[1])} for group in itertools.groupby(sorted_files_to_read, lambda f: f.last_modified)]
        return slices

    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        """
        schema = self._catalog_schema
        if schema is None:
            # On read requests we should always have the catalog available
            raise MissingSchemaError("Expected `json_schema` in the configured catalog but it is missing.")
        parser = self.get_parser(self.config.file_type)
        for file in stream_slice["files"]:
            # only serialize the datetime once
            file_datetime_string = file.last_modified.strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                for record in parser.parse_records(file, self._stream_reader):
                    if not record_passes_validation_policy(self.config.validation_policy, record, schema):
                        logging.warning(f"Record did not pass validation policy: {record}")
                        continue
                    record[self.ab_last_mod_col] = file_datetime_string
                    record[self.ab_file_name_col] = file.uri
                    yield stream_data_to_airbyte_message(self.name, record)
                self._cursor.add_file(file)
            except Exception as exc:
                raise RecordParseError(f"Error reading records from file: {file.uri}. Is the file valid {self.config.file_type}?") from exc

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        return self.ab_last_mod_col

    @cache
    def get_json_schema(self) -> Mapping[str, Any]:
        extra_fields = {
            self.ab_last_mod_col: {"type": "string"},
            self.ab_file_name_col: {"type": "string"},
        }
        schema = self._get_raw_json_schema()
        schema["properties"] = {**extra_fields, **schema.get("properties", {})}
        return schema

    def _get_raw_json_schema(self) -> Mapping[str, Any]:
        if self.config.input_schema:
            type_mapping = self.config.input_schema
        else:
            files = self._list_files()
            max_n_files_for_schema_inference = self._discovery_policy.max_n_files_for_schema_inference
            if len(files) > max_n_files_for_schema_inference:
                # Use the most recent files for schema inference, so we pick up schema changes during discovery.
                files = sorted(files, key=lambda x: x.last_modified, reverse=True)[:max_n_files_for_schema_inference]
                logging.warning(f"Refusing to infer schema for {len(files)} files; using {max_n_files_for_schema_inference} files.")
            type_mapping = self.infer_schema(files)
        return type_mapping

    @cache
    def _list_files(self) -> List[RemoteFile]:
        """
        List all files that belong to the stream as defined by the stream's globs.
        The output of this method is cached so we don't need to list the files more than once.
        This means we won't pick up changes to the files during a sync.
        """
        return list(self._stream_reader.get_matching_files(self.config.globs))

    def infer_schema(self, files: List[RemoteFile]) -> Mapping[str, Any]:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._infer_schema(files))

    async def _infer_schema(self, files: List[RemoteFile]) -> Mapping[str, Any]:
        """
        Infer the schema for a stream.

        Each file type has a corresponding `infer_schema` handler.
        Dispatch on file type.
        """
        base_schema = {}
        pending_tasks = set()

        n_started, n_files = 0, len(files)
        files = iter(files)
        while pending_tasks or n_started < n_files:
            while len(pending_tasks) <= self._discovery_policy.n_concurrent_requests and (file := next(files, None)):
                pending_tasks.add(asyncio.create_task(self._infer_file_schema(file)))
                n_started += 1
            # Return when the first task is completed so that we can enqueue a new task as soon as the
            # number of concurrent tasks drops below the number allowed.
            done, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                base_schema = merge_schemas(base_schema, task.result())

        return {"type": "object", "properties": base_schema}

    async def _infer_file_schema(self, file: RemoteFile) -> Mapping[str, Any]:
        try:
            return await self.get_parser(self.config.file_type).infer_schema(file, self._stream_reader)
        except Exception as exc:
            raise SchemaInferenceError(f"Error inferring schema for file: {file.uri}. Is the file valid {self.config.file_type}?") from exc
