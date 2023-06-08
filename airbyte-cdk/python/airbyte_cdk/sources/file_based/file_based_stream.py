#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import logging
import os
from functools import cache, cached_property
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.file_based.availability_strategy import FileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_concurrency_policy import AbstractDiscoveryConcurrencyPolicy
from airbyte_cdk.sources.file_based.exceptions import MissingSchemaError, SchemaInferenceError
from airbyte_cdk.sources.file_based.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types import AvroParser, CsvParser, FileTypeParser, JsonlParser, ParquetParser
from airbyte_cdk.sources.file_based.remote_file import FileType, RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import merge_schemas, type_mapping_to_jsonschema
from airbyte_cdk.sources.file_based.schema_validation_policies import record_passes_validation_policy
from airbyte_cdk.sources.streams import Stream

MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE = os.getenv("MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE", 10)


class FileBasedStream(Stream):
    """
    A file-based stream in an Airbyte source.

    In addition to the base Stream attributes, a file-based stream has
    - A config object (derived from the corresponding stream section in source config).
      This contains the globs defining the stream's files.
    - A StreamReader, which knows how to list and open files in the stream.
    - An AvailabilityStrategy, which knows how to verify that we can list and open
      files in the stream.
    """

    def __init__(
        self,
        raw_config: Dict[str, Any],
        stream_reader: AbstractFileBasedStreamReader,
        discovery_concurrency_policy: AbstractDiscoveryConcurrencyPolicy,
    ):
        self.config = FileBasedStreamConfig.from_raw_config(raw_config)
        self.catalog_schema = {}  # TODO: wire through configured catalog
        self.stream_reader = stream_reader
        self.discovery_concurrency_policy = discovery_concurrency_policy

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.config.primary_key

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        """
        schema = self.catalog_schema
        if schema is None:
            # On read requests we should always have the catalog available
            raise MissingSchemaError("Expected `json_schema` in the configured catalog but it is missing.")
        parser = self._get_parser(self.config.file_type)
        for file in self.list_files_for_this_sync(stream_state):
            for record in parser.parse_records(file, self.stream_reader):
                if not record_passes_validation_policy(self.config.validation_policy, record, schema):
                    logging.warning(f"Record did not pass validation policy: {record}")
                    continue
                yield record

    @cached_property
    def availability_strategy(self):
        return FileBasedAvailabilityStrategy(self.stream_reader)

    @property
    def name(self) -> str:
        return self.config.name

    @cache
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Return the JSON Schema for a stream.

        If the user provided a schema, return that. Otherwise, infer it.

        Use no more than MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE files.
        """
        if self.config.input_schema:
            return type_mapping_to_jsonschema(self.config.input_schema)

        files = self.list_files()
        if len(files) > MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE:
            files = sorted(files, key=lambda x: x.last_modified, reverse=True)[:MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE]
            logging.warning(f"Refusing to infer schema for {len(files)} files; using {MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE} files.")
        return self.infer_schema(files)

    @cache
    def list_files(self) -> List[RemoteFile]:
        """
        List all files that belong to the stream as defined by the stream's
        globs.
        """
        return list(self.stream_reader.list_matching_files(self.config.globs))

    def list_files_for_this_sync(self, stream_state: Mapping[str, Any]) -> Iterable[RemoteFile]:
        """
        Return the subset of this stream's files that will be read in the current sync.

        Specifically:

        - Take the output of `list_files`
        - If `stream_state.start` is non-None then remove all files with last_modified
          date before `start`
        """
        # TODO: implement me
        return iter(self.list_files())

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
            while len(pending_tasks) < self.discovery_concurrency_policy.n_concurrent_requests and (file := next(files, None)):
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
            return await self._get_parser(self.config.file_type).infer_schema(file, self.stream_reader)
        except Exception as exc:
            raise SchemaInferenceError(f"Error inferring schema for file: {file.uri}") from exc

    @staticmethod
    def _get_parser(file_type: FileType) -> FileTypeParser:
        return {
            FileType.Avro: AvroParser(),
            FileType.Csv: CsvParser(),
            FileType.Jsonl: JsonlParser(),
            FileType.Parquet: ParquetParser(),
        }[file_type]
