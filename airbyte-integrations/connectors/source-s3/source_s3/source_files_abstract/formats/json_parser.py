#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, BinaryIO, Iterator, Mapping, TextIO, Union

from pandas import DataFrame
from pandas.io.json import build_table_schema, read_json

from .abstract_file_parser import AbstractFileParser

# All possible json data types
JSON_TYPES = {
    # Table Schema type: (json_type, convert_function)
    # standard types
    "string": ("string", None),
    "boolean": ("boolean", None),
    "number": ("number", None),
    "integer": ("integer", None),
    # supported by Pandas type
    "datetime": ("string", lambda v: v.isoformat()),
    "duration": ("string", lambda v: v.isoformat()),
}


class JsonParser(AbstractFileParser):
    @property
    def is_binary(self) -> bool:
        return True

    def _read_options(self) -> Mapping[str, Any]:
        """
        https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#reading-json
        """
        return {
            "lines": self._format.get("lines", True),
            "chunksize": self._format.get("chunk_size", 10000),
            "nrows": self._format.get("nrows", None),
            "compression": self._format.get("compression", "infer"),
            "encoding": self._format.get("encoding", "utf8"),
        }

    def _parse_options(self) -> Mapping[str, Any]:
        """
        https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#reading-json
        """
        schema = self.json_schema_to_dtype_schema(self._master_schema) if self._master_schema is not None else None
        return {
            "dtype": schema,
            "convert_dates": self._format.get("convert_dates", True),
            "keep_default_dates": self._format.get("keep_default_dates", True),
            "orient": self._format.get("orient", "columns"),
        }

    @staticmethod
    def parse_field_type(needed_table_schema_type: str) -> str:
        """
        https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#table-schema
        Convert Table Schema types to Json types
        """
        if needed_table_schema_type not in JSON_TYPES:
            raise TypeError(f"Incorrect Table Schema type: {needed_table_schema_type}")
        else:
            json_type, _ = JSON_TYPES[needed_table_schema_type]
            return json_type

    @staticmethod
    def convert_field_data(table_schema_type: str, field_value: Any) -> Any:
        """Converts not JSON format to JSON one"""
        if field_value is None:
            return None
        if table_schema_type in JSON_TYPES:
            _, conversion_func = JSON_TYPES[table_schema_type]
            return conversion_func(field_value) if conversion_func else field_value
        raise TypeError(f"Unsupported field type: {table_schema_type}, value: {field_value}")

    def _build_table_schema(self, dataframe: DataFrame) -> dict:
        schema = build_table_schema(dataframe)
        # remove the first field which is the Pandas index
        schema_fields = schema["fields"][1:]

        return {field["name"]: field["type"] for field in schema_fields}

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """
        https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#reading-json
        """
        reader = read_json(file, **self._read_options(), **self._parse_options())

        is_lines_true = self._read_options()["lines"]
        if is_lines_true:
            dataframe = reader.read()
        else:
            dataframe = reader

        schema_dict = {
            field_name: self.parse_field_type(field_type) for (field_name, field_type) in self._build_table_schema(dataframe).items()
        }

        if not schema_dict:
            # pandas can parse empty JSON files but a connector can't generate dynamic schema
            raise OSError("empty JSON file")

        return schema_dict

    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """
        https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#reading-json
        Pandas reads streaming batches from a JSON line-delimited file
        """
        reader = read_json(
            file,
            **self._read_options(),
            **self._parse_options(),
        )

        # in case of classic JSON, put the whole dataframe in a list so the for loop
        # can be factorized with the iterator behaviour for line-delimited JSON
        reader = [reader] if not self._read_options()["lines"] else reader
        schema = None
        is_empty = True
        for rows in reader:
            schema = self._build_table_schema(rows) if schema is None else schema
            if is_empty and len(rows) > 0:
                is_empty = False
            for row in rows.to_dict(orient="records"):
                yield {k: self.convert_field_data(schema[k], v) for (k, v) in row.items()}
        if is_empty:
            raise OSError("Empty JSON file")
