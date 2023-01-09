#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, BinaryIO, Iterator, Mapping, TextIO, Union

import fastavro
from fastavro import reader
from source_s3.source_files_abstract.file_info import FileInfo

from .abstract_file_parser import AbstractFileParser

# mapping from apache avro docs: https://avro.apache.org/docs/current/spec.html#schema_complex
data_type_mapping = {
    "null": "null",
    "boolean": "boolean",
    "int": "integer",
    "long": "integer",
    "float": "number",
    "double": "number",
    "bytes": "string",
    "string": "string",
    "record": "object",
    "enum": "string",
    "array": "array",
    "map": "object",
    "fixed": "string",
}


class AvroParser(AbstractFileParser):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def is_binary(self) -> bool:
        return True

    def _parse_data_type(self, data_type_mapping: dict, avro_schema: dict) -> dict:
        """Convert data types from avro to json format
        :param data_type_mapping: mapping from avro to json data types
        :param avro_schema: schema comes with the avro file
        :return schema_dict with data types converted from avro to json standards
        """
        schema_dict = {}
        for i in avro_schema["fields"]:
            data_type = i["type"]
            # If field is nullable there will be a list of types and we need to make sure to map the whole list according to data_type_mapping
            if isinstance(data_type, list):
                schema_dict[i["name"]] = [data_type_mapping[dtype] for dtype in data_type]
            # TODO: Figure out a better way to handle nested records. Currently a nested record is returned as a string
            elif isinstance(data_type, dict):
                schema_dict[i["name"]] = "string"
            elif data_type in data_type_mapping:
                schema_dict[i["name"]] = data_type_mapping[data_type]
            else:
                raise TypeError(f"unsupported data type: {data_type} found in avro file")
        return schema_dict

    def _get_avro_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """Extract schema for records
        :param file: file-like object (opened via StorageFile)
        :return schema extracted from the avro file
        """
        avro_reader = fastavro.reader(file)
        schema = avro_reader.writer_schema
        if not schema["type"] == "record":
            unsupported_type = schema["type"]
            raise (f"Only record based avro files are supported. Found {unsupported_type}")
        else:
            return schema

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> dict:
        """Return schema
        :param file: file-like object (opened via StorageFile)
        :param file_info: file metadata
        :return: mapping of {columns:datatypes} where datatypes are JsonSchema types
        """
        avro_schema = self._get_avro_schema(file)
        schema_dict = self._parse_data_type(data_type_mapping, avro_schema)
        return schema_dict

    def stream_records(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> Iterator[Mapping[str, Any]]:
        """Stream the data using a generator
        :param file: file-like object (opened via StorageFile)
        :param file_info: file metadata
        :yield: data record as a mapping of {columns:values}
        """
        avro_reader = reader(file)
        for record in avro_reader:
            yield record
