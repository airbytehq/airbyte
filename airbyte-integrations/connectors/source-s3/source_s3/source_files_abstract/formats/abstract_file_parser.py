#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Iterator, Mapping, TextIO, Union

import pyarrow as pa
from airbyte_cdk.logger import AirbyteLogger
from source_s3.source_files_abstract.file_info import FileInfo


class AbstractFileParser(ABC):
    logger = AirbyteLogger()

    NON_SCALAR_TYPES = {"struct": "struct", "list": "list"}
    TYPE_MAP = {
        "boolean": ("bool_", "bool"),
        "integer": ("int64", "int8", "int16", "int32", "uint8", "uint16", "uint32", "uint64"),
        "number": ("float64", "float16", "float32", "decimal128", "decimal256", "halffloat", "float", "double"),
        "string": ("large_string", "string"),
        # TODO: support object type rather than coercing to string
        "object": ("large_string",),
        # TODO: support array type rather than coercing to string
        "array": ("large_string",),
        "null": ("large_string",),
    }

    def __init__(self, format: dict, master_schema: dict = None):
        """
        :param format: file format specific mapping as described in spec.json
        :param master_schema: superset schema determined from all files, might be unused for some formats, defaults to None
        """
        self._format = format
        self._master_schema = (
            master_schema
            # this may need to be used differently by some formats, pyarrow allows extra columns in csv schema
        )

    @property
    @abstractmethod
    def is_binary(self) -> bool:
        """
        Override this per format so that file-like objects passed in are currently opened as binary or not
        """

    @abstractmethod
    def get_inferred_schema(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> dict:
        """
        Override this with format-specifc logic to infer the schema of file
        Note: needs to return inferred schema with JsonSchema datatypes

        :param file: file-like object (opened via StorageFile)
        :param file_info: file metadata
        :return: mapping of {columns:datatypes} where datatypes are JsonSchema types
        """

    @abstractmethod
    def stream_records(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> Iterator[Mapping[str, Any]]:
        """
        Override this with format-specifc logic to stream each data row from the file as a mapping of {columns:values}
        Note: avoid loading the whole file into memory to avoid OOM breakages

        :param file: file-like object (opened via StorageFile)
        :param file_info: file metadata
        :yield: data record as a mapping of {columns:values}
        """

    @classmethod
    def json_type_to_pyarrow_type(cls, typ: str, reverse: bool = False, logger: AirbyteLogger = AirbyteLogger()) -> str:
        """
        Converts Json Type to PyArrow types to (or the other way around if reverse=True)

        :param typ: Json type if reverse is False, else PyArrow type
        :param reverse: switch to True for PyArrow type -> Json type, defaults to False
        :param logger: defaults to AirbyteLogger()
        :return: PyArrow type if reverse is False, else Json type
        """
        str_typ = str(typ)
        # This is a map of airbyte types to pyarrow types.
        # The first list element of the pyarrow types should be the one to use where required.

        if not reverse:
            for json_type, pyarrow_types in cls.TYPE_MAP.items():
                if str_typ.lower() == json_type:
                    type_ = next(iter(pyarrow_types))
                    if type_ in cls.NON_SCALAR_TYPES:
                        return cls.NON_SCALAR_TYPES[type_]
                    # better way might be necessary when we decide to handle more type complexity
                    return str(getattr(pa, type_).__call__())
            logger.debug(f"JSON type '{str_typ}' is not mapped, falling back to default conversion to large_string")
            return str(pa.large_string())
        else:
            for json_type, pyarrow_types in cls.TYPE_MAP.items():
                if any(str_typ.startswith(pa_type) for pa_type in pyarrow_types):
                    return json_type
            logger.debug(f"PyArrow type '{str_typ}' is not mapped, falling back to default conversion to string")
            return "string"  # default type if unspecified in map

    @classmethod
    def json_schema_to_pyarrow_schema(cls, schema: Mapping[str, Any], reverse: bool = False) -> Mapping[str, Any]:
        """
        Converts a schema with JsonSchema datatypes to one with PyArrow types (or the other way if reverse=True)
        This utilises json_type_to_pyarrow_type() to convert each datatype

        :param schema: json/pyarrow schema to convert
        :param reverse: switch to True for PyArrow schema -> Json schema, defaults to False
        :return: converted schema dict
        """
        return {column: cls.json_type_to_pyarrow_type(json_type, reverse=reverse) for column, json_type in schema.items()}

    def _validate_config(self, config: Mapping[str, Any]):
        pass
