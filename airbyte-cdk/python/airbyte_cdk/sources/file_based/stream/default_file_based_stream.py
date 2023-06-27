#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import logging
from datetime import datetime
from functools import cache
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.file_based.exceptions import MissingSchemaError, RecordParseError, SchemaInferenceError
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import merge_schemas, type_mapping_to_jsonschema
from airbyte_cdk.sources.file_based.schema_validation_policies import record_passes_validation_policy
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message


class DefaultFileBasedStream(AbstractFileBasedStream):
    """
    The default file-based stream.
    """

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.config.primary_key

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
        for file in self.list_files_for_this_sync(stream_slice):
            try:
                for record in parser.parse_records(file, self._stream_reader):
                    if not record_passes_validation_policy(self.config.validation_policy, record, schema):
                        logging.warning(f"Record did not pass validation policy: {record}")
                        continue
                    yield stream_data_to_airbyte_message(self.name, record)
            except Exception as exc:
                raise RecordParseError(f"Error reading records from file: {file.uri}. Is the file valid {self.config.file_type}?") from exc

    @cache
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Return the JSON Schema for a stream.

        If the user provided a schema, return that. Otherwise, infer it.

        Use no more than `_discovery_policy.max_n_files_for_schema_inference` files.
        """
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
        return list(self._stream_reader.get_matching_files(self.config.globs))

    def list_files_for_this_sync(self, stream_slice: Optional[StreamSlice]) -> Iterable[RemoteFile]:
        """
        Return the subset of this stream's files that will be read in the current sync.

        Specifically:

        - Take the output of `list_files`
        - If `stream_slice.start` is non-None then remove all files with last_modified
          date before `start`
        """
        yield from self._stream_reader.get_matching_files(self.config.globs, self._get_datetime_from_stream_slice(stream_slice))

    def _get_datetime_from_stream_slice(self, stream_slice: Optional[StreamSlice]) -> Optional[datetime]:
        # TODO: implement me
        return None

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
