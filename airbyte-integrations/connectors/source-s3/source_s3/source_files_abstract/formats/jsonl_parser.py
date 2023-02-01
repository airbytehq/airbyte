#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, BinaryIO, Iterator, Mapping, TextIO, Union

import pyarrow as pa
from pyarrow import ArrowNotImplementedError
from pyarrow import json as pa_json
from source_s3.source_files_abstract.file_info import FileInfo

from .abstract_file_parser import AbstractFileParser
from .jsonl_spec import JsonlFormat

logger = logging.getLogger("airbyte")


class JsonlParser(AbstractFileParser):
    TYPE_MAP = {
        "boolean": ("bool_", "bool"),
        "integer": ("int64", "int8", "int16", "int32", "uint8", "uint16", "uint32", "uint64"),
        "number": ("float64", "float16", "float32", "decimal128", "decimal256", "halffloat", "float", "double"),
        "string": ("large_string", "string"),
        # TODO: support object type rather than coercing to string
        "object": (
            "struct",
            "large_string",
        ),
        # TODO: support array type rather than coercing to string
        "array": (
            "list",
            "large_string",
        ),
        "null": ("large_string",),
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.format_model = None

    @property
    def is_binary(self) -> bool:
        return True

    @property
    def format(self) -> JsonlFormat:
        if self.format_model is None:
            self.format_model = JsonlFormat.parse_obj(self._format)
        return self.format_model

    def _read_options(self) -> Mapping[str, str]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.json.ReadOptions.html
        build ReadOptions object like: pa.json.ReadOptions(**self._read_options())
        Disable block size parameter if it set to 0.
        """
        return {**{"block_size": self.format.block_size if self.format.block_size else None, "use_threads": True}}

    def _parse_options(self, json_schema: Mapping[str, Any] = None) -> Mapping[str, str]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.json.ParseOptions.html
        build ParseOptions object like: pa.json.ParseOptions(**self._parse_options())
        :param json_schema: if this is passed in, pyarrow will attempt to enforce this schema on read, defaults to None
        """
        parse_options = {
            "newlines_in_values": self.format.newlines_in_values,
            "unexpected_field_behavior": self.format.unexpected_field_behavior,
        }
        if json_schema:
            schema = self.json_schema_to_pyarrow_schema(json_schema)
            schema = pa.schema({field: type_ for field, type_ in schema.items() if type_ not in self.NON_SCALAR_TYPES.values()})
            parse_options["explicit_schema"] = schema
        return parse_options

    def _read_table(self, file: Union[TextIO, BinaryIO], json_schema: Mapping[str, Any] = None) -> pa.Table:
        try:
            return pa_json.read_json(
                file, pa.json.ReadOptions(**self._read_options()), pa.json.ParseOptions(**self._parse_options(json_schema))
            )
        except ArrowNotImplementedError as e:
            message = "Possibly too small block size used. Please try to increase it or set to 0 disable this feature."
            logger.warning(message)
            raise ValueError(message) from e

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> Mapping[str, Any]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.json.read_json.html
        Json reader support multi thread hence, donot need to add external process
        https://arrow.apache.org/docs/python/generated/pyarrow.json.ReadOptions.html
        """

        def field_type_to_str(type_: Any) -> str:
            if isinstance(type_, pa.lib.StructType):
                return "struct"
            if isinstance(type_, pa.lib.ListType):
                return "list"
            if isinstance(type_, pa.lib.DataType):
                return str(type_)
            raise Exception(f"Unknown PyArrow Type: {type_}")

        table = self._read_table(file)
        schema_dict = {field.name: field_type_to_str(field.type) for field in table.schema}
        return self.json_schema_to_pyarrow_schema(schema_dict, reverse=True)

    def stream_records(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> Iterator[Mapping[str, Any]]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.json.read_json.html

        """
        table = self._read_table(file, self._master_schema)
        yield from table.to_pylist()
