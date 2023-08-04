#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import json
import logging
from collections import defaultdict
from functools import partial
from io import IOBase
from typing import Any, Callable, Dict, Generator, Iterable, List, Mapping, Optional, Set

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


class _CsvReader:
    def read_data(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        file_read_mode: FileReadMode,
    ) -> Generator[Dict[str, Any], None, None]:
        config_format = _extract_config_format(config)

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
        with stream_reader.open_file(file, file_read_mode, logger) as fp:
            headers = self._get_headers(fp, config_format, dialect_name)

            fp.seek(0)
            # we assume that if we autogenerate columns, it is because we don't have headers
            # if a user wants to autogenerate_column_names with a CSV having headers, he can skip rows
            rows_to_skip = config_format.skip_rows_before_header + (0 if config_format.autogenerate_column_names else 1) + config_format.skip_rows_after_header
            self._skip_rows(fp, rows_to_skip)

            reader = csv.DictReader(fp, dialect=dialect_name, fieldnames=headers)  # type: ignore
            try:
                for row in reader:
                    # The row was not properly parsed if any of the values are None. This will most likely occur if there are more columns than
                    # headers
                    if None in row:
                        raise RecordParseError(FileBasedSourceError.ERROR_PARSING_RECORD)
                    yield row
            finally:
                # due to RecordParseError or GeneratorExit
                csv.unregister_dialect(dialect_name)

    def _get_headers(self, fp: IOBase, config_format: CsvFormat, dialect_name: str) -> List[str]:
        # Note that this method assumes the dialect has already been registered if we're parsing the headers
        self._skip_rows(fp, config_format.skip_rows_before_header)
        if config_format.autogenerate_column_names:
            return self._auto_generate_headers(fp, config_format, dialect_name)
        else:
            # Then read the header
            reader = csv.reader(fp, dialect=dialect_name)  # type: ignore
            return list(next(reader))

    def _auto_generate_headers(self, fp: IOBase, config_format: CsvFormat, dialect_name: str) -> List[str]:
        """
        Generates field names as [f0, f1, ...] in the same way as pyarrow's csv reader with autogenerate_column_names=True.
        See https://arrow.apache.org/docs/python/generated/pyarrow.csv.ReadOptions.html
        """
        reader = csv.reader(fp, dialect=dialect_name)  # type: ignore
        number_of_columns = len(next(reader))  # type: ignore
        # Reset the file pointer to the beginning of the file so that the first row is not skipped
        fp.seek(0)
        return [f"f{i}" for i in range(number_of_columns)]

    @staticmethod
    def _skip_rows(fp: IOBase, rows_to_skip: int) -> None:
        """
        Skip rows before the header. This has to be done on the file object itself, not the reader
        """
        for _ in range(rows_to_skip):
            fp.readline()


class CsvParser(FileTypeParser):
    _MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE = 1_000_000

    def __init__(self, csv_reader: Optional[_CsvReader] = None):
        self._csv_reader = csv_reader if csv_reader else _CsvReader()

    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Dict[str, Any]:
        # todo: the existing InMemoryFilesSource.open_file() test source doesn't currently require an encoding, but actual
        #  sources will likely require one. Rather than modify the interface now we can wait until the real use case
        config_format = _extract_config_format(config)
        type_inferrer_by_field: Dict[str, _TypeInferrer] = defaultdict(
            lambda: _TypeInferrer(config_format.true_values, config_format.false_values)
        )
        data_generator = self._csv_reader.read_data(config, file, stream_reader, logger, self.file_read_mode)
        read_bytes = 0
        for row in data_generator:
            for header, value in row.items():
                type_inferrer_by_field[header].add_value(value)
                # This is not accurate as a representation of how many bytes were read because csv does some processing on the actual value
                # before returning. Given we would like to be more accurate, we could wrap the IO file using a decorator
                read_bytes += len(value)
            read_bytes += len(row) - 1  # for separators
            if read_bytes >= self._MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE:
                break

        schema = {header.strip(): {"type": type_inferred.infer()} for header, type_inferred in type_inferrer_by_field.items()}
        data_generator.close()
        return schema

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Dict[str, Any]]:
        schema: Mapping[str, Any] = config.input_schema  # type: ignore
        config_format = _extract_config_format(config)
        cast_fn = CsvParser._get_cast_function(schema, config_format, logger)
        data_generator = self._csv_reader.read_data(config, file, stream_reader, logger, self.file_read_mode)
        for row in data_generator:
            yield CsvParser._to_nullable(cast_fn(row), config_format.null_values)
        data_generator.close()

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ

    @staticmethod
    def _get_cast_function(
        schema: Optional[Mapping[str, Any]], config_format: CsvFormat, logger: logging.Logger
    ) -> Callable[[Mapping[str, str]], Mapping[str, str]]:
        # Only cast values if the schema is provided
        if schema:
            property_types = {col: prop["type"] for col, prop in schema["properties"].items()}
            return partial(CsvParser._cast_types, property_types=property_types, config_format=config_format, logger=logger)
        else:
            # If no schema is provided, yield the rows as they are
            return _no_cast

    @staticmethod
    def _to_nullable(row: Mapping[str, str], null_values: Set[str]) -> Dict[str, Optional[str]]:
        nullable = row | {k: None if v in null_values else v for k, v in row.items()}
        return nullable

    @staticmethod
    def _cast_types(row: Dict[str, str], property_types: Dict[str, Any], config_format: CsvFormat, logger: logging.Logger) -> Dict[str, Any]:
        """
        Casts the values in the input 'row' dictionary according to the types defined in the JSON schema.

        Array and object types are only handled if they can be deserialized as JSON.

        If any errors are encountered, the value will be emitted as a string._to_nullable
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
                        # we don't re-use _value_to_object here because we type the column as object as long as there is only one object
                        cast_value = json.loads(value)
                    except json.JSONDecodeError:
                        warnings.append(_format_warning(key, value, prop_type))

                elif python_type == list:
                    try:
                        cast_value = _value_to_list(value)
                    except (ValueError, json.JSONDecodeError):
                        warnings.append(_format_warning(key, value, prop_type))

                elif python_type:
                    try:
                        cast_value = _value_to_python_type(value, python_type)
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


class _TypeInferrer:
    _BOOLEAN_TYPE = "boolean"
    _NUMBER_TYPE = "number"
    _ARRAY_TYPE = "array"
    _OBJECT_TYPE = "object"
    _STRING_TYPE = "string"

    def __init__(self, boolean_trues: Set[str], boolean_falses: Set[str]) -> None:
        self._boolean_trues = boolean_trues
        self._boolean_falses = boolean_falses
        self._values: Set[str] = set()

    def add_value(self, value: Any) -> None:
        self._values.add(value)

    def infer(self) -> str:
        types = {self._infer_type(value) for value in self._values}

        if types == {self._BOOLEAN_TYPE}:
            return self._BOOLEAN_TYPE
        elif types == {self._NUMBER_TYPE}:
            return self._NUMBER_TYPE
        elif types == {self._ARRAY_TYPE}:
            return self._ARRAY_TYPE
        elif self._ARRAY_TYPE in types or self._OBJECT_TYPE in types:
            return self._OBJECT_TYPE
        return self._STRING_TYPE

    def _infer_type(self, value: str) -> str:
        if self._is_boolean(value):
            return self._BOOLEAN_TYPE
        elif self._is_number(value):
            return self._NUMBER_TYPE
        elif self._is_array(value):
            return self._ARRAY_TYPE
        elif self._is_object(value):
            return self._OBJECT_TYPE
        else:
            return self._STRING_TYPE

    def _is_boolean(self, value: str) -> bool:
        try:
            _value_to_bool(value, self._boolean_trues, self._boolean_falses)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_number(value: str) -> bool:
        try:
            _value_to_python_type(value, float)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_array(value: str) -> bool:
        try:
            _value_to_list(value)
            return True
        except (ValueError, json.JSONDecodeError):
            return False

    @staticmethod
    def _is_object(value: str) -> bool:
        try:
            _value_to_object(value)
            return True
        except (ValueError, json.JSONDecodeError):
            return False


def _value_to_bool(value: str, true_values: Set[str], false_values: Set[str]) -> bool:
    if value in true_values:
        return True
    if value in false_values:
        return False
    raise ValueError(f"Value {value} is not a valid boolean value")


def _value_to_object(value: str) -> Dict[Any, Any]:
    parsed_value = json.loads(value)
    if isinstance(parsed_value, dict):
        return parsed_value
    raise ValueError(f"Value {parsed_value} is not a valid dict value")


def _value_to_list(value: str) -> List[Any]:
    parsed_value = json.loads(value)
    if isinstance(parsed_value, list):
        return parsed_value
    raise ValueError(f"Value {parsed_value} is not a valid list value")


def _value_to_python_type(value: str, python_type: type) -> Any:
    return python_type(value)


def _format_warning(key: str, value: str, expected_type: Optional[Any]) -> str:
    return f"{key}: value={value},expected_type={expected_type}"


def _no_cast(row: Mapping[str, str]) -> Mapping[str, str]:
    return row


def _extract_config_format(config: FileBasedStreamConfig) -> CsvFormat:
    config_format = config.format.get(config.file_type) if config.format else CsvFormat()
    if not isinstance(config_format, CsvFormat):
        raise ValueError(f"Invalid format config: {config_format}")
    return config_format
