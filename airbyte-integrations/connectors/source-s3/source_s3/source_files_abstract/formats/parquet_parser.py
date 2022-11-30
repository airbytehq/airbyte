#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, BinaryIO, Iterator, List, Mapping, TextIO, Tuple, Union

import pyarrow.parquet as pq
from airbyte_cdk.models import FailureType
from pyarrow.parquet import ParquetFile
from source_s3.exceptions import S3Exception
from source_s3.source_files_abstract.file_info import FileInfo

from .abstract_file_parser import AbstractFileParser
from .parquet_spec import ParquetFormat

# All possible parquet data types
PARQUET_TYPES = {
    # logical_type: (json_type, parquet_types, convert_function)
    # standard types
    "string": ("string", ["BYTE_ARRAY"], None),
    "boolean": ("boolean", ["BOOLEAN"], None),
    "number": ("number", ["DOUBLE", "FLOAT"], None),
    "integer": ("integer", ["INT32", "INT64", "INT96"], None),
    "decimal": ("number", ["INT32", "INT64", "FIXED_LEN_BYTE_ARRAY"], None),
    # supported by PyArrow types
    "timestamp": ("string", ["INT32", "INT64", "INT96"], lambda v: v.isoformat()),
    "date": ("string", ["INT32", "INT64", "INT96"], lambda v: v.isoformat()),
    "time": ("string", ["INT32", "INT64", "INT96"], lambda v: v.isoformat()),
}


class ParquetParser(AbstractFileParser):
    """Apache Parquet is a free and open-source column-oriented data storage format of the Apache Hadoop ecosystem.

    Docs: https://parquet.apache.org/documentation/latest/
    """

    is_binary = True

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        # adds default values if necessary attributes are skipped.
        for field_name, field in ParquetFormat.__fields__.items():
            if self._format.get(field_name) is not None:
                continue
            self._format[field_name] = field.default

    def _select_options(self, *names: List[str]) -> dict:
        return {name: self._format[name] for name in names}

    def _init_reader(self, file: Union[TextIO, BinaryIO]) -> ParquetFile:
        """Generates a new parquet reader
        Doc: https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html

        """
        options = self._select_options("buffer_size")  # type: ignore[arg-type]
        # Source is a file path and enabling memory_map can improve performance in some environments.
        options["memory_map"] = True
        return pq.ParquetFile(file, **options)

    @staticmethod
    def parse_field_type(needed_logical_type: str, need_physical_type: str = None) -> Tuple[str, str]:
        """Pyarrow can parse/support non-JSON types
        Docs: https://github.com/apache/arrow/blob/5aa2901beddf6ad7c0a786ead45fdb7843bfcccd/python/pyarrow/_parquet.pxd#L56
        """
        if needed_logical_type not in PARQUET_TYPES:
            # by default the pyarrow library marks scalar types as 'none' logical type.
            # For these cases we need to look for by a physical type
            for logical_type, (json_type, physical_types, _) in PARQUET_TYPES.items():
                if need_physical_type in physical_types:
                    return json_type, logical_type
        else:
            json_type, physical_types, _ = PARQUET_TYPES[needed_logical_type]
            if need_physical_type and need_physical_type not in physical_types:
                raise TypeError(f"incorrect parquet physical type: {need_physical_type}; logical type: {needed_logical_type}")
            return json_type, needed_logical_type

        raise TypeError(f"incorrect parquet physical type: {need_physical_type}; logical type: {needed_logical_type}")

    @staticmethod
    def convert_field_data(logical_type: str, field_value: Any) -> Any:
        """Converts not JSON format to JSON one"""
        if field_value is None:
            return None
        if logical_type in PARQUET_TYPES:
            _, _, func = PARQUET_TYPES[logical_type]
            return func(field_value) if func else field_value
        raise TypeError(f"unsupported field type: {logical_type}, value: {field_value}")

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> dict:
        """
        https://arrow.apache.org/docs/python/parquet.html#finer-grained-reading-and-writing

        A stored schema is a part of metadata and we can extract it without parsing of full file
        """
        reader = self._init_reader(file)
        schema_dict = {
            field.name: self.parse_field_type(field.logical_type.type.lower(), field.physical_type)[0] for field in reader.schema
        }
        if not schema_dict:
            # pyarrow can parse empty parquet files but a connector can't generate dynamic schema
            raise S3Exception(file_info, "empty Parquet file", "The .parquet file is empty!", FailureType.config_error)
        return schema_dict

    def stream_records(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> Iterator[Mapping[str, Any]]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html
        PyArrow reads streaming batches from a Parquet file
        """

        reader = self._init_reader(file)
        self.logger.info(f"found {reader.num_row_groups} row groups")
        # parsing logical_types with respect to master_schema column names.
        logical_types = {
            field.name: self.parse_field_type(field.logical_type.type.lower(), field.physical_type)[1]
            for field in reader.schema
            if field.name in self._master_schema
        }
        if not reader.schema:
            # pyarrow can parse empty parquet files but a connector can't generate dynamic schema
            raise S3Exception(file_info, "empty Parquet file", "The .parquet file is empty!", FailureType.config_error)

        args = self._select_options("columns", "batch_size")  # type: ignore[arg-type]
        self.logger.debug(f"Found the {reader.num_row_groups} Parquet groups")

        # load batches per page
        for num_row_group in range(reader.num_row_groups):
            args["row_groups"] = [num_row_group]
            for batch in reader.iter_batches(**args):
                # this gives us a dist of lists where each nested list holds ordered values for a single column
                # {'number': [1.0, 2.0, 3.0], 'name': ['foo', None, 'bar'], 'flag': [True, False, True], 'delta': [-1.0, 2.5, 0.1]}
                batch_dict = batch.to_pydict()
                # sometimes the batch file has more columns than master_schema declares, like:
                # master schema: ['number', 'name', 'flag', 'delta'],
                # batch_file_schema: ['number', 'name', 'flag', 'delta', 'EXTRA_COL_NAME'].
                # we need to check wether batch_file_schema == master_schema and reject extra columns, otherwise "KeyError" raises.
                batch_columns = [column for column in batch_dict.keys() if column in self._master_schema]
                columnwise_record_values = [batch_dict[column] for column in batch_columns if column in self._master_schema]
                # we zip this to get row-by-row
                for record_values in zip(*columnwise_record_values):
                    yield {
                        batch_columns[i]: self.convert_field_data(logical_types[batch_columns[i]], record_values[i])
                        for i in range(len(batch_columns))
                    }
