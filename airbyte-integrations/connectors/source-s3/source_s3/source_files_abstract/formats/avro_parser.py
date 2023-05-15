#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, BinaryIO, Iterator, Mapping, TextIO, Union

import fastavro
from fastavro import reader
from source_s3.source_files_abstract.file_info import FileInfo

from .abstract_file_parser import AbstractFileParser

# mapping from apache avro docs: https://avro.apache.org/docs/current/spec.html#schema_complex
AVRO_TO_JSON_DATA_TYPE_MAPPING = {
    "null": "null",
    "boolean": ["boolean", "null"],
    "int": ["integer", "null"],
    "long": ["integer", "null"],
    "float": ["number", "null"],
    "double": ["number", "null"],
    "bytes": ["string", "null"],
    "string": ["string", "null"],
    "record": ["object", "null"],
    "enum": ["string", "null"],
    "array": ["array", "null"],
    "map": ["object", "null"],
    "fixed": ["string", "null"],
}


class AvroParser(AbstractFileParser):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @property
    def is_binary(self) -> bool:
        return True

    def avro_type_to_json_type(self, avro_type):
        try:
            return AVRO_TO_JSON_DATA_TYPE_MAPPING[avro_type]
        except KeyError:
            raise ValueError(f"Unknown Avro type: {avro_type}")

    def avro_to_jsonschema(self, avro_schema: dict) -> dict:
        """Convert data types from avro to json format
        :param avro_schema: schema comes with the avro file
        :return schema_dict with data types converted from avro to json standards
        """
        json_schema = {}
        # Process Avro schema fields
        for field in avro_schema["fields"]:
            field_name = field["name"]
            field_type = field["type"]
            # Convert Avro types to JSON schema types
            if isinstance(field_type, dict) and field_type.get("type") == "array":
                field_schema = {"type": ["array", "null"], "items": self.avro_to_jsonschema(field_type.get("items"))}
            elif isinstance(field_type, dict):
                field_schema = {"type": ["object", "null"], **self.avro_to_jsonschema(field_type)}
            elif isinstance(field_type, list) and [x.get("fields") for x in field_type if not isinstance(x, str)]:
                # field_type = [x for x in field_type if x != 'null'][0]
                field_schema = {"anyOf": [self.avro_to_jsonschema(t) for t in field_type]}
            else:
                field_type = [x for x in field_type if x != "null"][0] if isinstance(field_type, list) else field_type
                field_schema = {"type": self.avro_type_to_json_type(field_type)}
            json_schema[field_name] = field_schema
        return json_schema

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
        :return: mapping of JsonSchema properties {columns:{"type": datatypes}}
        """
        avro_schema = self._get_avro_schema(file)
        schema_dict = self.avro_to_jsonschema(avro_schema)
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
