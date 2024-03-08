#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import itertools
import traceback
from copy import deepcopy
from functools import cache
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Set, Union

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, FailureType, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.file_based.config.file_based_stream_config import PrimaryKeyType
from airbyte_cdk.sources.file_based.exceptions import (
    FileBasedSourceError,
    InvalidSchemaError,
    MissingSchemaError,
    NoFilesMatchingError,
    RecordParseError,
    SchemaInferenceError,
    StopSyncPerValidationPolicy,
)
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType, merge_schemas, schemaless_schema
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.file_based.stream.cursor import AbstractFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamSlice
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import JsonSchema
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class DefaultFileBasedStream(AbstractFileBasedStream, IncrementalMixin):

    """
    The default file-based stream.
    """

    DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    ab_last_mod_col = "_ab_source_file_last_modified"
    ab_file_name_col = "_ab_source_file_url"
    airbyte_columns = [ab_last_mod_col, ab_file_name_col]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._cursor.get_state()

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        """State setter, accept state serialized by state getter."""
        self._cursor.set_initial_state(value)

    @property
    def cursor(self) -> Optional[AbstractFileBasedCursor]:
        return self._cursor

    @cursor.setter
    def cursor(self, value: AbstractFileBasedCursor) -> None:
        if self._cursor is not None:
            raise RuntimeError(f"Cursor for stream {self.name} is already set. This is unexpected. Please contact Support.")
        self._cursor = value

    @property
    def primary_key(self) -> PrimaryKeyType:
        return self.config.primary_key or self.get_parser().get_parser_defined_primary_key(self.config)

    def compute_slices(self) -> Iterable[Optional[Mapping[str, Any]]]:
        # Sort files by last_modified, uri and return them grouped by last_modified
        all_files = self.list_files()
        files_to_read = self._cursor.get_files_to_sync(all_files, self.logger)
        sorted_files_to_read = sorted(files_to_read, key=lambda f: (f.last_modified, f.uri))
        slices = [{"files": list(group[1])} for group in itertools.groupby(sorted_files_to_read, lambda f: f.last_modified)]
        return slices

    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[AirbyteMessage]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.

        If an error is encountered reading records from a file, log a message and do not attempt
        to sync the rest of the file.
        """
        schema = self.catalog_schema
        if schema is None:
            # On read requests we should always have the catalog available
            raise MissingSchemaError(FileBasedSourceError.MISSING_SCHEMA, stream=self.name)
        # The stream only supports a single file type, so we can use the same parser for all files
        parser = self.get_parser()
        for file in stream_slice["files"]:
            # only serialize the datetime once
            file_datetime_string = file.last_modified.strftime(self.DATE_TIME_FORMAT)
            n_skipped = line_no = 0

            try:
                for record in parser.parse_records(self.config, file, self.stream_reader, self.logger, schema):
                    line_no += 1
                    if self.config.schemaless:
                        record = {"data": record}
                    elif not self.record_passes_validation_policy(record):
                        n_skipped += 1
                        continue
                    record[self.ab_last_mod_col] = file_datetime_string
                    record[self.ab_file_name_col] = file.uri
                    yield stream_data_to_airbyte_message(self.name, record)
                self._cursor.add_file(file)

            except StopSyncPerValidationPolicy:
                yield AirbyteMessage(
                    type=MessageType.LOG,
                    log=AirbyteLogMessage(
                        level=Level.WARN,
                        message=f"Stopping sync in accordance with the configured validation policy. Records in file did not conform to the schema. stream={self.name} file={file.uri} validation_policy={self.config.validation_policy.value} n_skipped={n_skipped}",
                    ),
                )
                break

            except RecordParseError:
                # Increment line_no because the exception was raised before we could increment it
                line_no += 1
                self.errors_collector.collect(
                    AirbyteMessage(
                        type=MessageType.LOG,
                        log=AirbyteLogMessage(
                            level=Level.ERROR,
                            message=f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream={self.name} file={file.uri} line_no={line_no} n_skipped={n_skipped}",
                            stack_trace=traceback.format_exc(),
                        ),
                    ),
                )

            except AirbyteTracedException as exc:
                # Re-raise the exception to stop the whole sync immediately as this is a fatal error
                raise exc

            except Exception:
                yield AirbyteMessage(
                    type=MessageType.LOG,
                    log=AirbyteLogMessage(
                        level=Level.ERROR,
                        message=f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream={self.name} file={file.uri} line_no={line_no} n_skipped={n_skipped}",
                        stack_trace=traceback.format_exc(),
                    ),
                )

            finally:
                if n_skipped:
                    yield AirbyteMessage(
                        type=MessageType.LOG,
                        log=AirbyteLogMessage(
                            level=Level.WARN,
                            message=f"Records in file did not pass validation policy. stream={self.name} file={file.uri} n_skipped={n_skipped} validation_policy={self.validation_policy.name}",
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
        except (InvalidSchemaError, NoFilesMatchingError) as config_exception:
            self.logger.exception(FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value, exc_info=config_exception)
            raise AirbyteTracedException(
                internal_message="Please check the logged errors for more information.",
                message=FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value,
                exception=AirbyteTracedException(exception=config_exception),
                failure_type=FailureType.config_error,
            )
        except Exception as exc:
            raise SchemaInferenceError(FileBasedSourceError.SCHEMA_INFERENCE_ERROR, stream=self.name) from exc
        else:
            return {"type": "object", "properties": {**extra_fields, **schema["properties"]}}

    def _get_raw_json_schema(self) -> JsonSchema:
        if self.config.input_schema:
            return self.config.get_input_schema()  # type: ignore
        elif self.config.schemaless:
            return schemaless_schema
        else:
            files = self.list_files()
            total_n_files = len(files)

            if total_n_files == 0:
                raise NoFilesMatchingError(FileBasedSourceError.EMPTY_STREAM, stream=self.name)

            max_n_files_for_schema_inference = self._discovery_policy.get_max_n_files_for_schema_inference(self.get_parser())
            if total_n_files > max_n_files_for_schema_inference:
                # Use the most recent files for schema inference, so we pick up schema changes during discovery.
                files = sorted(files, key=lambda x: x.last_modified, reverse=True)[:max_n_files_for_schema_inference]
                self.logger.warn(
                    msg=f"Refusing to infer schema for all {total_n_files} files; using {max_n_files_for_schema_inference} files."
                )

            inferred_schema = self.infer_schema(files)

            if not inferred_schema:
                raise InvalidSchemaError(
                    FileBasedSourceError.INVALID_SCHEMA_ERROR,
                    details=f"Empty schema. Please check that the files are valid for format {self.config.format}",
                    stream=self.name,
                )

            schema = {"type": "object", "properties": inferred_schema}

        return schema

    def get_files(self) -> Iterable[RemoteFile]:
        """
        Return all files that belong to the stream as defined by the stream's globs.
        """
        return self.stream_reader.get_matching_files(self.config.globs or [], self.config.legacy_prefix, self.logger)

    def infer_schema(self, files: List[RemoteFile]) -> Mapping[str, Any]:
        loop = asyncio.get_event_loop()
        schema = loop.run_until_complete(self._infer_schema(files))
        # as infer schema returns a Mapping that is assumed to be immutable, we need to create a deepcopy to avoid modifying the reference
        return self._fill_nulls(deepcopy(schema))

    @staticmethod
    def _fill_nulls(schema: Mapping[str, Any]) -> Mapping[str, Any]:
        if isinstance(schema, dict):
            for k, v in schema.items():
                if k == "type":
                    if isinstance(v, list):
                        if "null" not in v:
                            schema[k] = ["null"] + v
                    elif v != "null":
                        schema[k] = ["null", v]
                else:
                    DefaultFileBasedStream._fill_nulls(v)
        elif isinstance(schema, list):
            for item in schema:
                DefaultFileBasedStream._fill_nulls(item)
        return schema

    async def _infer_schema(self, files: List[RemoteFile]) -> Mapping[str, Any]:
        """
        Infer the schema for a stream.

        Each file type has a corresponding `infer_schema` handler.
        Dispatch on file type.
        """
        base_schema: SchemaType = {}
        pending_tasks: Set[asyncio.tasks.Task[SchemaType]] = set()

        n_started, n_files = 0, len(files)
        files_iterator = iter(files)
        while pending_tasks or n_started < n_files:
            while len(pending_tasks) <= self._discovery_policy.n_concurrent_requests and (file := next(files_iterator, None)):
                pending_tasks.add(asyncio.create_task(self._infer_file_schema(file)))
                n_started += 1
            # Return when the first task is completed so that we can enqueue a new task as soon as the
            # number of concurrent tasks drops below the number allowed.
            done, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                try:
                    base_schema = merge_schemas(base_schema, task.result())
                except Exception as exc:
                    self.logger.error(f"An error occurred inferring the schema. \n {traceback.format_exc()}", exc_info=exc)

        return base_schema

    async def _infer_file_schema(self, file: RemoteFile) -> SchemaType:
        try:
            return await self.get_parser().infer_schema(self.config, file, self.stream_reader, self.logger)
        except Exception as exc:
            raise SchemaInferenceError(
                FileBasedSourceError.SCHEMA_INFERENCE_ERROR,
                file=file.uri,
                format=str(self.config.format),
                stream=self.name,
            ) from exc
