#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, BinaryIO, Iterator, Mapping, TextIO, Union

import pandas as pd
import pyarrow as pa
from pyarrow import ArrowInvalid, ArrowNotImplementedError
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
    CAN_TYPECAST = {
        "integer": int,
        "number": int,
        "string": str,
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

    def apply_typecasting(
        self,
        data: dict,
        column_path,
        cast_type: str,
        current_path_key_idx: int,
    ):
        if current_path_key_idx == len(column_path) - 1:
            # column to be typecasted
            current_column = column_path[-1]
            data[current_column] = self.CAN_TYPECAST[cast_type](data[current_column])
            return
        current_column = column_path[current_path_key_idx]
        if current_column == "[]":
            for value in data:
                self.apply_typecasting(value, column_path, cast_type, current_path_key_idx + 1)
        else:
            self.apply_typecasting(data[current_column], column_path, cast_type, current_path_key_idx + 1)

    def _reformat_table(self, data: pd.DataFrame, json_schema: Mapping[str, Any] = None) -> pa.Table:
        if json_schema:
            # example json schema = {"event":"object","event/user_attributes/Mobile Phone Number":"number"}
            top_level_key = list(json_schema.keys())[0]
            for column, d_type in list(json_schema.items())[1:]:
                if d_type in self.CAN_TYPECAST:
                    column_path_list = column.split("/")
                    if column_path_list[0] != top_level_key:
                        logger.error("incorrect top level key or column path")
                        raise ValueError("incorrect top level key or column path")

                    for value in data[top_level_key]:
                        # start from first index zeroth index is for top level key
                        self.apply_typecasting(value, column_path_list, d_type, 1)
        # reset index, by default pandas add integer indexes
        data.reset_index(drop=True, inplace=True)
        return pa.Table.from_pandas(data)

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

        try:
            table = self._read_table(file)
        except ArrowInvalid:
            logger.warning("warning: mixed json types in data")
            # move to begining of file
            file.seek(0)
            if self.format.block_size:
                chunks_data = pd.read_json(file, lines=True, chunksize=self.format.block_size)
                for data in chunks_data:
                    table = self._reformat_table(data.to_dict(), self._master_schema).to_pylist()
                    break
            else:
                chunks_data = pd.read_json(file, lines=True)
                table = self._reformat_table(chunks_data, self._master_schema).to_pylist()
        schema_dict = {field.name: field_type_to_str(field.type) for field in table.schema}
        return self.json_schema_to_pyarrow_schema(schema_dict, reverse=True)

    def stream_records(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> Iterator[Mapping[str, Any]]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.json.read_json.html

        """
        try:
            yield from self._read_table(file, self._master_schema).to_pylist()
        except ArrowInvalid:
            logger.warning("warning: mixed json types in data")
            # move to begining of file
            file.seek(0)
            if self.format.block_size:
                chunks_data = pd.read_json(file, lines=True, chunksize=self.format.block_size)
                for data in chunks_data:
                    yield from self._reformat_table(data.to_dict(), self._master_schema).to_pylist()
            else:
                chunks_data = pd.read_json(file, lines=True)
                yield from self._reformat_table(chunks_data, self._master_schema).to_pylist()

    @classmethod
    def set_minimal_block_size(cls, format: Mapping[str, Any]):
        format["block_size"] = 0
