#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from typing import Any, BinaryIO, Iterator, List, Mapping, TextIO, Union

import pyarrow.parquet as pq
from pyarrow.parquet import ParquetFile

from .abstract_file_parser import AbstractFileParser
from .parquet_spec import ParquetFormat

# All possible parquet data typess
PARQUET_TYPES = {
    "BOOLEAN": "boolean",
    "DOUBLE": "number",
    "FLOAT": "number",
    "BYTE_ARRAY": "string",
    "INT32": "integer",
    "INT64": "integer",
    "INT96": "integer",
}


class ParquetParser(AbstractFileParser):
    """Apache Parquet is a free and open-source column-oriented data storage format of the Apache Hadoop ecosystem.

    Docs: https://parquet.apache.org/documentation/latest/
    """

    is_binary = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # adds default values if necessary attributes are skipped.
        for field_name, field in ParquetFormat.__fields__.items():
            if self._format.get(field_name) is not None:
                continue
            self._format[field_name] = field.default

    def _select_options(self, *names: List[str]) -> dict:
        return {name: self._format[name] for name in names}

    def _init_reader(self, file: BinaryIO) -> ParquetFile:
        """Generates a new parquet reader
        Doc: https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html

        """
        options = self._select_options(
            "buffer_size",
        )
        # Source is a file path and enabling memory_map can improve performance in some environments.
        options["memory_map"] = True
        return pq.ParquetFile(file, **options)

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """
        https://arrow.apache.org/docs/python/parquet.html#finer-grained-reading-and-writing

        A stored schema is a part of metadata and we can extract it without parsing of full file
        """
        reader = self._init_reader(file)
        schema_dict = {field.name: PARQUET_TYPES[field.physical_type] for field in reader.schema}
        if not schema_dict:
            # pyarrow can parse empty parquet files but a connector can't generate dynamic schema
            raise OSError("empty Parquet file")
        return schema_dict

    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html
        PyArrow reads streaming batches from a Parquet file
        """

        reader = self._init_reader(file)
        self.logger.info(f"found {reader.num_row_groups} row groups")

        if not reader.schema:
            # pyarrow can parse empty parquet files but a connector can't generate dynamic schema
            raise OSError("empty Parquet file")

        args = self._select_options("columns", "batch_size")
        num_row_groups = list(range(reader.num_row_groups))

        # load batches per page
        for num_row_group in num_row_groups:
            args["row_groups"] = [num_row_group]
            for batch in reader.iter_batches(**args):
                # this gives us a dist of lists where each nested list holds ordered values for a single column
                # {'number': [1.0, 2.0, 3.0], 'name': ['foo', None, 'bar'], 'flag': [True, False, True], 'delta': [-1.0, 2.5, 0.1]}
                batch_columns = [col.name for col in batch.schema]
                batch_dict = batch.to_pydict()
                columnwise_record_values = [batch_dict[column] for column in batch_columns]

                # we zip this to get row-by-row
                for record_values in zip(*columnwise_record_values):
                    yield {batch_columns[i]: record_values[i] for i in range(len(batch_columns))}
