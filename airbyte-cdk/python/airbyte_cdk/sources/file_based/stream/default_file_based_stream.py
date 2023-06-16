#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import itertools
import logging
from datetime import datetime, timedelta, time
from functools import cache
from typing import Any, Iterable, List, Mapping, Optional, Union, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.file_based.exceptions import MissingSchemaError, RecordParseError, SchemaInferenceError
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import merge_schemas, type_mapping_to_jsonschema
from airbyte_cdk.sources.file_based.schema_validation_policies import record_passes_validation_policy
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.file_based.stream.file_based_state import FileBasedState
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message


class DefaultFileBasedStream(AbstractFileBasedStream, IncrementalMixin):
    """
    The default file-based stream.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # FIXME: move ot a policy or something
        self._state = FileBasedState(self.config.max_history_size or 10_000, timedelta(days=(self.config.days_to_sync_if_history_is_full or 3)))

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state.to_dict()

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self._state.set_initial_state(value)

    # FIXME These things should probably be in a policy
    ab_last_mod_col = "_ab_source_file_last_modified"
    ab_file_name_col = "_ab_source_file_url"
    airbyte_columns = [ab_last_mod_col, ab_file_name_col]

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.config.primary_key

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # WARNING: The stream state passed here is NOT used !!!
        # FIXME: Should probably be in a policy
        # Step 1: Get all files that match a glob (no filtering yet)
        # Step 2: Filter out files that have already been processed
        files = [{"uri": f.uri,
                  "last_modified": f.last_modified,
                  "file_type": f.file_type} for f in self.list_files_for_this_sync()]

        return [{"files": list(group[1])} for group in itertools.groupby(files, lambda f: f['last_modified'])]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[StreamState] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        """
        schema = self._catalog_schema
        if schema is None:
            # On read requests we should always have the catalog available
            raise MissingSchemaError("Expected `json_schema` in the configured catalog but it is missing.")
        parser = self.get_parser(self.config.file_type)
        for file_description in stream_slice["files"]:
            file = RemoteFile.from_file_partition(file_description)
            try:
                for record in parser.parse_records(file, self._stream_reader):
                    if not record_passes_validation_policy(self.config.validation_policy, record, schema):
                        logging.warning(f"Record did not pass validation policy: {record}")
                        continue
                    yield stream_data_to_airbyte_message(self.name, record)
                self._state.add_file(file)
            except Exception as exc:
                raise RecordParseError(
                    f"Error reading records from file: {file_description['uri']}. Is the file valid {self.config.file_type}?"
                ) from exc

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        # FIXME: should be in a policy
        return self.ab_last_mod_col

    @cache
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Return the JSON Schema for a stream.

        If the user provided a schema, return that. Otherwise, infer it.

        Use no more than `_discovery_policy.max_n_files_for_schema_inference` files.
        """
        # FIXME: need to merge with additional columns
        if self.config.input_schema:
            return type_mapping_to_jsonschema(self.config.input_schema)

        files = self.list_files()
        max_n_files_for_schema_inference = self._discovery_policy.max_n_files_for_schema_inference
        if len(files) > max_n_files_for_schema_inference:
            # Use the most recent files for schema inference, so we pick up schema changes during discovery.
            files = sorted(files, key=lambda x: x.last_modified, reverse=True)[:max_n_files_for_schema_inference]
            logging.warning(f"Refusing to infer schema for {len(files)} files; using {max_n_files_for_schema_inference} files.")
        return self.infer_schema(files)

    @cache
    def list_files(self) -> List[RemoteFile]:
        """
        List all files that belong to the stream as defined by the stream's globs.
        """
        return list(self._stream_reader.list_matching_files(self.config.globs))

    def list_files_for_this_sync(self) -> Iterable[RemoteFile]:
        """
        Return the subset of this stream's files that will be read in the current sync.

        Specifically:

        - Take the output of `list_files`
        - If `stream_slice.start` is non-None then remove all files with last_modified
          date before `start`
        """

        """
        Only sync files newer than (3?) days,  
        or equal to or newer than the oldest file(s) recorded in the history
        """
        all_files = self._stream_reader.list_matching_files(self.config.globs)
        return self._state.get_files_to_sync(all_files)

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

        return base_schema

    async def _infer_file_schema(self, file: RemoteFile) -> Mapping[str, Any]:
        try:
            return await self.get_parser(self.config.file_type).infer_schema(file, self._stream_reader)
        except Exception as exc:
            raise SchemaInferenceError(f"Error inferring schema for file: {file.uri}. Is the file valid {self.config.file_type}?") from exc
