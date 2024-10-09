#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Dict, Generator, Iterable, Mapping, Optional
from uuid import uuid4


from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.writers.file_based_stream_writer import AbstractFileBasedStreamWriter
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType


class _FileReader:
    def read_data(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        file_read_mode: FileReadMode,
    ) -> Generator[Dict[str, Any], None, None]:

        try:
            file_size = stream_reader.file_size(file)
            with stream_reader.open_file(file, file_read_mode, "UTF-8", logger) as fp:
                yield fp, file_size

        except Exception as ex:
            logger.error("An error has occurred while reading file: %s", str(ex))

class BlobTransfer(FileTypeParser):
    def __init__(self, file_reader: Optional[_FileReader] = None):
        self._file_reader = file_reader if file_reader else _FileReader()

    def write_streams(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        stream_writer: AbstractFileBasedStreamWriter = None,
    ) -> Iterable[Dict[str, Any]]:
        file_no = 0
        try:
            data_generator = self._file_reader.read_data(config, file, stream_reader, logger, self.file_read_mode)
            for file_opened, file_size in data_generator:
                yield from stream_writer.write(file.uri, file_opened, file_size, logger)
                file_no += 1
        except RecordParseError as parse_err:
            raise RecordParseError(FileBasedSourceError.ERROR_PARSING_RECORD, filename=file.uri, lineno=file_no) from parse_err
        finally:
            data_generator.close()

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ

    def get_parser_defined_primary_key(self, config: FileBasedStreamConfig) -> Optional[str]:
        ...

    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ):
        ...

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        discovered_schema: Optional[Mapping[str, SchemaType]],
    ):
        ...

    def check_config(self, config: FileBasedStreamConfig):
        ...
