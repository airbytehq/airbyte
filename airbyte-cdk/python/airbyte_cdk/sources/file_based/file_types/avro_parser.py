#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Dict, Iterable, Mapping

import fastavro
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile

AVRO_TYPE_TO_JSON_TYPE = {
    "null": "null",
    "boolean": "boolean",
    "int": "integer",
    "long": "integer",
    "float": "number",
    "double": "string",  # double -> number conversions can lose precision
    "bytes": "string",
    "string": "string",
}

AVRO_LOGICAL_TYPE_TO_JSON = {
    "decimal": {"type": "string"},
    "date": {"type": "string", "format": "date"},
    "time-millis": {"type": "integer"},
    "time-micros": {"type": "integer"},
    "timestamp-millis": {"type": "string", "format": "date-time"},
    "timestamp-micros": {"type": "string"},
    # fastavro does not support duration https://fastavro.readthedocs.io/en/latest/logical_types.html
}


class AvroParser(FileTypeParser):
    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Dict[str, Any]:
        avro_reader = fastavro.reader(stream_reader.open_file(file))
        avro_schema = avro_reader.writer_schema
        if not avro_schema["type"] == "record":
            unsupported_type = avro_schema["type"]
            raise ValueError(f"Only record based avro files are supported. Found {unsupported_type}")
        json_schema = {
            field["name"]: AvroParser._convert_avro_type_to_json(field["name"], field["type"]) for field in avro_schema["fields"]
        }
        return json_schema

    @classmethod
    def _convert_avro_type_to_json(cls, field_name: str, avro_field: str) -> Mapping[str, Any]:
        if isinstance(avro_field, Mapping) and avro_field["type"] == "record":
            return {
                "type": "object",
                "properties": {
                    object_field["name"]: {**AvroParser._convert_avro_type_to_json(object_field["name"], object_field["type"])}
                    for object_field in avro_field["fields"]
                },
            }
        elif isinstance(avro_field, Mapping) and avro_field["type"] == "array":
            if "items" not in avro_field:
                raise ValueError(f"{field_name} array type does not have a required field items")
            return {"type": "array", "items": {**AvroParser._convert_avro_type_to_json("", avro_field["items"])}}
        elif isinstance(avro_field, Mapping) and avro_field["type"] == "enum":
            if "symbols" not in avro_field:
                raise ValueError(f"{field_name} enum type does not have a required field symbols")
            if "name" not in avro_field:
                raise ValueError(f"{field_name} enum type does not have a required field name")
            return {"type": "string", "enum": avro_field["symbols"]}
        elif isinstance(avro_field, Mapping) and avro_field["type"] == "map":
            if "values" not in avro_field:
                raise ValueError(f"{field_name} map type does not have a required field values")
            return {"type": "object", "additionalProperties": {**AvroParser._convert_avro_type_to_json("", avro_field["values"])}}
        elif isinstance(avro_field, Mapping) and avro_field["type"] == "fixed" and avro_field.get("logicalType") != "duration":
            if "size" not in avro_field:
                raise ValueError(f"{field_name} fixed type does not have a required field size")
            if not isinstance(avro_field["size"], int):
                raise ValueError(f"{field_name} fixed type size value is not an integer")
            return {
                "type": "string",
                "pattern": f"^[0-9A-Fa-f]{{{avro_field['size'] * 2}}}$",
            }
        elif isinstance(avro_field, Mapping) and avro_field.get("logicalType") == "decimal":
            if "precision" not in avro_field:
                raise ValueError(f"{field_name} decimal type does not have a required field precision")
            if "scale" not in avro_field:
                raise ValueError(f"{field_name} decimal type does not have a required field scale")
            max_whole_number_range = avro_field["precision"] - avro_field["scale"]
            decimal_range = avro_field["scale"]

            # This regex looks like a mess, but it is validation for at least one whole number and optional fractional numbers
            # For example: ^-?\d{1,5}(?:\.\d{1,3})?$ would accept 12345.123 and 123456.12345 would  be rejected
            return {"type": "string", "pattern": f"^-?\\d{{{1,max_whole_number_range}}}(?:\\.\\d{1,decimal_range})?$"}
        elif isinstance(avro_field, Mapping) and "logicalType" in avro_field:
            if avro_field["logicalType"] not in AVRO_LOGICAL_TYPE_TO_JSON:
                raise ValueError(f"{avro_field['logical_type']} is not a valid Avro logical type")
            return AVRO_LOGICAL_TYPE_TO_JSON[avro_field["logicalType"]]
        elif avro_field in AVRO_TYPE_TO_JSON_TYPE:
            return {"type": AVRO_TYPE_TO_JSON_TYPE[avro_field]}
        else:
            raise ValueError(f"Unsupported avro type: {avro_field}")

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Dict[str, Any]]:
        avro_reader = fastavro.reader(stream_reader.open_file(file))
        for record in avro_reader:
            yield record
