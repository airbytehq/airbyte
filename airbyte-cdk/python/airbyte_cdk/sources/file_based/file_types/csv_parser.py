#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import json
import logging
from functools import partial
from io import IOBase
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Set

from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat, QuotingBehavior
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import TYPE_PYTHON_MAPPING

DIALECT_NAME = "_config_dialect"

config_to_quoting: Mapping[QuotingBehavior, int] = {
    QuotingBehavior.QUOTE_ALL: csv.QUOTE_ALL,
    QuotingBehavior.QUOTE_SPECIAL_CHARACTERS: csv.QUOTE_MINIMAL,
    QuotingBehavior.QUOTE_NONNUMERIC: csv.QUOTE_NONNUMERIC,
    QuotingBehavior.QUOTE_NONE: csv.QUOTE_NONE,
}


class CsvParser(FileTypeParser):
    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Dict[str, Any]:
        config_format = config.format.get(config.file_type) if config.format else CsvFormat()
        if not isinstance(config_format, CsvFormat):
            raise ValueError(f"Invalid format config: {config_format}")
        dialect_name = config.name + DIALECT_NAME
        csv.register_dialect(
            dialect_name,
            delimiter=config_format.delimiter,
            quotechar=config_format.quote_char,
            escapechar=config_format.escape_char,
            doublequote=config_format.double_quote,
            quoting=config_to_quoting.get(config_format.quoting_behavior, csv.QUOTE_MINIMAL),
        )
        with stream_reader.open_file(file, self.file_read_mode, logger) as fp:
            # todo: the existing InMemoryFilesSource.open_file() test source doesn't currently require an encoding, but actual
            #  sources will likely require one. Rather than modify the interface now we can wait until the real use case
            headers = self._get_headers(fp, config_format, dialect_name)
            schema = {field.strip(): {"type": "string"} for field in headers}
            csv.unregister_dialect(dialect_name)
            return schema

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Dict[str, Any]]:
        schema: Mapping[str, Any] = config.input_schema  # type: ignore
        config_format = config.format.get(config.file_type) if config.format else CsvFormat()
        if not isinstance(config_format, CsvFormat):
            raise ValueError(f"Invalid format config: {config_format}")
        # Formats are configured individually per-stream so a unique dialect should be registered for each stream.
        # We don't unregister the dialect because we are lazily parsing each csv file to generate records
        # This will potentially be a problem if we ever process multiple streams concurrently
        dialect_name = config.name + DIALECT_NAME
        csv.register_dialect(
            dialect_name,
            delimiter=config_format.delimiter,
            quotechar=config_format.quote_char,
            escapechar=config_format.escape_char,
            doublequote=config_format.double_quote,
            quoting=config_to_quoting.get(config_format.quoting_behavior, csv.QUOTE_MINIMAL),
        )
        with stream_reader.open_file(file, self.file_read_mode, logger) as fp:
            # todo: the existing InMemoryFilesSource.open_file() test source doesn't currently require an encoding, but actual
            #  sources will likely require one. Rather than modify the interface now we can wait until the real use case
            self._skip_rows_before_header(fp, config_format.skip_rows_before_header)
            field_names = self._auto_generate_headers(fp, config_format) if config_format.autogenerate_column_names else None
            reader = csv.DictReader(fp, dialect=dialect_name, fieldnames=field_names)  # type: ignore
            yield from self._read_and_cast_types(reader, schema, config_format, logger)

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ

    @staticmethod
    def _read_and_cast_types(
        reader: csv.DictReader, schema: Optional[Mapping[str, Any]], config_format: CsvFormat, logger: logging.Logger  # type: ignore
    ) -> Iterable[Dict[str, Any]]:
        """
        If the user provided a schema, attempt to cast the record values to the associated type.

        If a column is not in the schema or cannot be cast to an appropriate python type,
        cast it to a string. Downstream, the user's validation policy will determine whether the
        record should be emitted.
        """
        cast_fn = CsvParser._get_cast_function(schema, config_format, logger)
        for i, row in enumerate(reader):
            if i < config_format.skip_rows_after_header:
                continue
            # The row was not properly parsed if any of  the values are None
            if any(val is None for val in row.values()):
                raise RecordParseError(FileBasedSourceError.ERROR_PARSING_RECORD)
            else:
                yield CsvParser._to_nullable(cast_fn(row), config_format.null_values)

    @staticmethod
    def _get_cast_function(
        schema: Optional[Mapping[str, Any]], config_format: CsvFormat, logger: logging.Logger
    ) -> Callable[[Mapping[str, str]], Mapping[str, str]]:
        # Only cast values if the schema is provided
        if schema:
            property_types = {col: prop["type"] for col, prop in schema["properties"].items()}
            return partial(_cast_types, property_types=property_types, config_format=config_format, logger=logger)
        else:
            # If no schema is provided, yield the rows as they are
            return _no_cast

    @staticmethod
    def _to_nullable(row: Mapping[str, str], null_values: Set[str]) -> Dict[str, Optional[str]]:
        nullable = row | {k: None if v in null_values else v for k, v in row.items()}
        return nullable

    @staticmethod
    def _skip_rows_before_header(fp: IOBase, rows_to_skip: int) -> None:
        """
        Skip rows before the header. This has to be done on the file object itself, not the reader
        """
        for _ in range(rows_to_skip):
            fp.readline()

    def _get_headers(self, fp: IOBase, config_format: CsvFormat, dialect_name: str) -> List[str]:
        # Note that this method assumes the dialect has already been registered if we're parsing the headers
        if config_format.autogenerate_column_names:
            return self._auto_generate_headers(fp, config_format)
        else:
            # If we're not autogenerating column names, we need to skip the rows before the header
            self._skip_rows_before_header(fp, config_format.skip_rows_before_header)
            # Then read the header
            reader = csv.DictReader(fp, dialect=dialect_name)  # type: ignore
            return next(reader)  # type: ignore

    def _auto_generate_headers(self, fp: IOBase, config_format: CsvFormat) -> List[str]:
        """
        Generates field names as [f0, f1, ...] in the same way as pyarrow's csv reader with autogenerate_column_names=True.
        See https://arrow.apache.org/docs/python/generated/pyarrow.csv.ReadOptions.html
        """
        next_line = next(fp).strip()
        number_of_columns = len(next_line.split(config_format.delimiter))  # type: ignore
        # Reset the file pointer to the beginning of the file so that the first row is not skipped
        fp.seek(0)
        return [f"f{i}" for i in range(number_of_columns)]


def _cast_types(row: Dict[str, str], property_types: Dict[str, Any], config_format: CsvFormat, logger: logging.Logger) -> Dict[str, Any]:
    """
    Casts the values in the input 'row' dictionary according to the types defined in the JSON schema.

    Array and object types are only handled if they can be deserialized as JSON.

    If any errors are encountered, the value will be emitted as a string.
    """
    warnings = []
    result = {}

    for key, value in row.items():
        prop_type = property_types.get(key)
        cast_value: Any = value

        if prop_type in TYPE_PYTHON_MAPPING and prop_type is not None:
            _, python_type = TYPE_PYTHON_MAPPING[prop_type]

            if python_type is None:
                if value == "":
                    cast_value = None
                else:
                    warnings.append(_format_warning(key, value, prop_type))

            elif python_type == bool:
                try:
                    cast_value = _value_to_bool(value, config_format.true_values, config_format.false_values)
                except ValueError:
                    warnings.append(_format_warning(key, value, prop_type))

            elif python_type == dict:
                try:
                    cast_value = json.loads(value)
                except json.JSONDecodeError:
                    warnings.append(_format_warning(key, value, prop_type))

            elif python_type == list:
                try:
                    parsed_value = json.loads(value)
                    if isinstance(parsed_value, list):
                        cast_value = parsed_value
                except json.JSONDecodeError:
                    warnings.append(_format_warning(key, value, prop_type))

            elif python_type:
                try:
                    cast_value = python_type(value)
                except ValueError:
                    warnings.append(_format_warning(key, value, prop_type))

        else:
            warnings.append(_format_warning(key, value, prop_type))

        result[key] = cast_value

    if warnings:
        logger.warning(
            f"{FileBasedSourceError.ERROR_CASTING_VALUE.value}: {','.join([w for w in warnings])}",
        )
    return result


def _value_to_bool(value: str, true_values: Set[str], false_values: Set[str]) -> bool:
    if value in true_values:
        return True
    if value in false_values:
        return False
    raise ValueError(f"Value {value} is not a valid boolean value")


def _format_warning(key: str, value: str, expected_type: Optional[Any]) -> str:
    return f"{key}: value={value},expected_type={expected_type}"


def _no_cast(row: Mapping[str, str]) -> Mapping[str, str]:
    return row
