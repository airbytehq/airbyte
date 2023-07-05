#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig, QuotingBehavior
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile

DIALECT_NAME = "_config_dialect"

config_to_quoting: [QuotingBehavior, int] = {
    QuotingBehavior.QUOTE_ALL: csv.QUOTE_ALL,
    QuotingBehavior.QUOTE_SPECIAL_CHARACTERS: csv.QUOTE_MINIMAL,
    QuotingBehavior.QUOTE_NONNUMERIC: csv.QUOTE_NONNUMERIC,
    QuotingBehavior.QUOTE_NONE: csv.QUOTE_NONE,
}


class CsvParser(FileTypeParser):
    async def infer_schema(
        self, config: FileBasedStreamConfig, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader
    ) -> Dict[str, Any]:
        config_format = config.format.get(config.file_type) if config.format else None
        if config_format:
            dialect_name = config.name + DIALECT_NAME
            csv.register_dialect(
                dialect_name,
                delimiter=config_format.delimiter,
                quotechar=config_format.quote_char,
                escapechar=config_format.escape_char,
                doublequote=config_format.double_quote,
                quoting=config_to_quoting.get(config_format.quoting_behavior, csv.QUOTE_MINIMAL),
            )
            with stream_reader.open_file(file) as fp:
                # todo: the existing InMemoryFilesSource.open_file() test source doesn't currently require an encoding, but actual
                #  sources will likely require one. Rather than modify the interface now we can wait until the real use case
                reader = csv.DictReader(fp, dialect=dialect_name)
                schema = {field.strip(): {"type": ["null", "string"]} for field in next(reader)}
                csv.unregister_dialect(dialect_name)
                return schema
        else:
            with stream_reader.open_file(file) as fp:
                reader = csv.DictReader(fp)
                return {field.strip(): {"type": ["null", "string"]} for field in next(reader)}

    def parse_records(
        self, config: FileBasedStreamConfig, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader
    ) -> Iterable[Dict[str, Any]]:
        config_format = config.format.get(config.file_type) if config.format else None
        if config_format:
            # Formats are configured individually per-stream so a unique dialect should be registered for each stream.
            # Wwe don't unregister the dialect because we are lazily parsing each csv file to generate records
            dialect_name = config.name + DIALECT_NAME
            csv.register_dialect(
                dialect_name,
                delimiter=config_format.delimiter,
                quotechar=config_format.quote_char,
                escapechar=config_format.escape_char,
                doublequote=config_format.double_quote,
                quoting=config_to_quoting.get(config_format.quoting_behavior, csv.QUOTE_MINIMAL),
            )
            with stream_reader.open_file(file) as fp:
                # todo: the existing InMemoryFilesSource.open_file() test source doesn't currently require an encoding, but actual
                #  sources will likely require one. Rather than modify the interface now we can wait until the real use case
                reader = csv.DictReader(fp, dialect=dialect_name)
                yield from reader
        else:
            with stream_reader.open_file(file) as fp:
                reader = csv.DictReader(fp)
                yield from reader
