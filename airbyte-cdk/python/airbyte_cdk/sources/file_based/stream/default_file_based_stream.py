#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import itertools
import logging
import traceback
from functools import cache
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type
from airbyte_cdk.sources.file_based.exceptions import (
    FileBasedSourceError,
    InvalidSchemaError,
    MissingSchemaError,
    SchemaInferenceError,
    StopSyncPerValidationPolicy,
)
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import merge_schemas
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.file_based.stream.cursor import FileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamSlice
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import JsonSchema
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
        all_files = self.list_files()
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
            raise MissingSchemaError(FileBasedSourceError.MISSING_SCHEMA, stream=self.name)
        parser = self.get_parser(self.config.file_type)
        for file in stream_slice["files"]:
            # only serialize the datetime once
            file_datetime_string = file.last_modified.strftime("%Y-%m-%dT%H:%M:%SZ")
            n_skipped = line_no = 0

            try:
                for record in parser.parse_records(self.config, file, self._stream_reader):
                    line_no += 1

                    if not self.record_passes_validation_policy(record):
                        n_skipped += 1
                        continue
                    record[self.ab_last_mod_col] = file_datetime_string
                    record[self.ab_file_name_col] = file.uri
                    yield stream_data_to_airbyte_message(self.name, record)
                self._cursor.add_file(file)

            except StopSyncPerValidationPolicy:
                yield AirbyteMessage(
                    type=Type.LOG,
                    log=AirbyteLogMessage(
                        level=Level.INFO,
                        message=f"Stopping sync in accordance with the configured validation policy. Records in file did not conform to the schema. stream={self.name} file={file.uri} validation_policy={self.config.validation_policy} n_skipped={n_skipped}",
                    ),
                )
                break

            except Exception as exc:
                yield AirbyteMessage(
                    type=Type.LOG,
                    log=AirbyteLogMessage(
                        level=Level.ERROR,
                        message=f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream={self.name} file={file.uri} line_no={line_no} n_skipped={n_skipped}",
                        stack_trace="\n".join(traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)),
                    ),
                )

            else:
                if n_skipped:
                    yield AirbyteMessage(
                        type=Type.LOG,
                        log=AirbyteLogMessage(
                            level=Level.INFO,
                            message=f"Records in file did not pass validation policy. stream={self.name} file={file.uri} n_skipped={n_skipped} validation_policy={self.config.validation_policy}",
                        ),
                    )

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        return self.ab_last_mod_col

    @cache
    def get_json_schema(self) -> JsonSchema:
        extra_fields = {
            self.ab_last_mod_col: {"type": "string"},
            self.ab_file_name_col: {"type": "string"},
        }
        try:
            schema = self._get_raw_json_schema()
        except Exception as exc:
            raise SchemaInferenceError(FileBasedSourceError.SCHEMA_INFERENCE_ERROR, stream=self.name) from exc
        else:
            if not schema:
                raise InvalidSchemaError(
                    FileBasedSourceError.INVALID_SCHEMA_ERROR,
                    details=f"Empty schema. Please check that the files are valid {self.config.file_type}",
                    stream=self.name,
                )
            return {"type": "object", "properties": {**extra_fields, **schema}}

    def _get_raw_json_schema(self) -> JsonSchema:
        if self.config.input_schema:
            schema = self.config.input_schema
        else:
            files = self.list_files()
            max_n_files_for_schema_inference = self._discovery_policy.max_n_files_for_schema_inference
            if len(files) > max_n_files_for_schema_inference:
                # Use the most recent files for schema inference, so we pick up schema changes during discovery.
                files = sorted(files, key=lambda x: x.last_modified, reverse=True)[:max_n_files_for_schema_inference]
                logging.warning(f"Refusing to infer schema for {len(files)} files; using {max_n_files_for_schema_inference} files.")
            schema = self.infer_schema(files)

        return schema

    @cache
    def list_files(self) -> List[RemoteFile]:
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
        base_schema: Dict[str, str] = {}
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
            return await self.get_parser(self.config.file_type).infer_schema(self.config, file, self._stream_reader)
        except Exception as exc:
            raise SchemaInferenceError(
                FileBasedSourceError.SCHEMA_INFERENCE_ERROR,
                file=file.uri,
                stream_file_type=self.config.file_type,
                stream=self.name,
            ) from exc
