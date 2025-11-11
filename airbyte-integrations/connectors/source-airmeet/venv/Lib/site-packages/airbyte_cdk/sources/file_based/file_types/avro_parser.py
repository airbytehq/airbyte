#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, cast

import fastavro

from airbyte_cdk.sources.file_based.config.avro_format import AvroFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import (
    AbstractFileBasedStreamReader,
    FileReadMode,
)
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType

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
    "uuid": {"type": "string"},
    "date": {"type": "string", "format": "date"},
    "time-millis": {"type": "integer"},
    "time-micros": {"type": "integer"},
    "timestamp-millis": {"type": "string", "format": "date-time"},
    "timestamp-micros": {"type": "string"},
    "local-timestamp-millis": {"type": "string", "format": "date-time"},
    "local-timestamp-micros": {"type": "string"},
    # fastavro does not support duration https://fastavro.readthedocs.io/en/latest/logical_types.html
}


class AvroParser(FileTypeParser):
    ENCODING = None

    def check_config(self, config: FileBasedStreamConfig) -> Tuple[bool, Optional[str]]:
        """
        AvroParser does not require config checks, implicit pydantic validation is enough.
        """
        return True, None

    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
        avro_format = config.format
        if not isinstance(avro_format, AvroFormat):
            raise ValueError(f"Expected ParquetFormat, got {avro_format}")

        with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:
            avro_reader = fastavro.reader(fp)  # type: ignore [arg-type]
            avro_schema = avro_reader.writer_schema
        if not avro_schema["type"] == "record":  # type: ignore [index, call-overload]
            unsupported_type = avro_schema["type"]  # type: ignore [index, call-overload]
            raise ValueError(
                f"Only record based avro files are supported. Found {unsupported_type}"
            )
        json_schema = {
            field["name"]: AvroParser._convert_avro_type_to_json(  # type: ignore [index]
                avro_format,
                field["name"],  # type: ignore [index]
                field["type"],  # type: ignore [index]
            )
            for field in avro_schema["fields"]  # type: ignore [index, call-overload]
        }
        return json_schema

    @classmethod
    def _convert_avro_type_to_json(
        cls, avro_format: AvroFormat, field_name: str, avro_field: str
    ) -> Mapping[str, Any]:
        if isinstance(avro_field, str) and avro_field in AVRO_TYPE_TO_JSON_TYPE:
            # Legacy behavior to retain backwards compatibility. Long term we should always represent doubles as strings
            if avro_field == "double" and not avro_format.double_as_string:
                return {"type": "number"}
            return {"type": AVRO_TYPE_TO_JSON_TYPE[avro_field]}
        if isinstance(avro_field, Mapping):
            if avro_field["type"] == "record":
                return {
                    "type": "object",
                    "properties": {
                        object_field["name"]: AvroParser._convert_avro_type_to_json(
                            avro_format, object_field["name"], object_field["type"]
                        )
                        for object_field in avro_field["fields"]
                    },
                }
            elif avro_field["type"] == "array":
                if "items" not in avro_field:
                    raise ValueError(
                        f"{field_name} array type does not have a required field items"
                    )
                return {
                    "type": "array",
                    "items": AvroParser._convert_avro_type_to_json(
                        avro_format, "", avro_field["items"]
                    ),
                }
            elif avro_field["type"] == "enum":
                if "symbols" not in avro_field:
                    raise ValueError(
                        f"{field_name} enum type does not have a required field symbols"
                    )
                if "name" not in avro_field:
                    raise ValueError(f"{field_name} enum type does not have a required field name")
                return {"type": "string", "enum": avro_field["symbols"]}
            elif avro_field["type"] == "map":
                if "values" not in avro_field:
                    raise ValueError(f"{field_name} map type does not have a required field values")
                return {
                    "type": "object",
                    "additionalProperties": AvroParser._convert_avro_type_to_json(
                        avro_format, "", avro_field["values"]
                    ),
                }
            elif avro_field["type"] == "fixed" and avro_field.get("logicalType") != "duration":
                if "size" not in avro_field:
                    raise ValueError(f"{field_name} fixed type does not have a required field size")
                if not isinstance(avro_field["size"], int):
                    raise ValueError(f"{field_name} fixed type size value is not an integer")
                return {
                    "type": "string",
                    "pattern": f"^[0-9A-Fa-f]{{{avro_field['size'] * 2}}}$",
                }
            elif avro_field.get("logicalType") == "decimal":
                if "precision" not in avro_field:
                    raise ValueError(
                        f"{field_name} decimal type does not have a required field precision"
                    )
                if "scale" not in avro_field:
                    raise ValueError(
                        f"{field_name} decimal type does not have a required field scale"
                    )
                max_whole_number_range = avro_field["precision"] - avro_field["scale"]
                decimal_range = avro_field["scale"]

                # This regex looks like a mess, but it is validation for at least one whole number and optional fractional numbers
                # For example: ^-?\d{1,5}(?:\.\d{1,3})?$ would accept 12345.123 and 123456.12345 would  be rejected
                return {
                    "type": "string",
                    "pattern": f"^-?\\d{{{1, max_whole_number_range}}}(?:\\.\\d{1, decimal_range})?$",
                }
            elif "logicalType" in avro_field:
                if avro_field["logicalType"] not in AVRO_LOGICAL_TYPE_TO_JSON:
                    raise ValueError(
                        f"{avro_field['logicalType']} is not a valid Avro logical type"
                    )
                return AVRO_LOGICAL_TYPE_TO_JSON[avro_field["logicalType"]]
            else:
                raise ValueError(f"Unsupported avro type: {avro_field}")
        else:
            raise ValueError(f"Unsupported avro type: {avro_field}")

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        discovered_schema: Optional[Mapping[str, SchemaType]],
    ) -> Iterable[Dict[str, Any]]:
        avro_format = config.format or AvroFormat(filetype="avro")
        if not isinstance(avro_format, AvroFormat):
            raise ValueError(f"Expected ParquetFormat, got {avro_format}")

        line_no = 0
        try:
            with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:
                avro_reader = fastavro.reader(fp)  # type: ignore [arg-type]
                schema = avro_reader.writer_schema
                schema_field_name_to_type = {
                    field["name"]: cast(dict[str, Any], field["type"])  # type: ignore [index]
                    for field in schema["fields"]  # type: ignore [index, call-overload]  # If schema is not dict, it is not subscriptable by strings
                }
                for record in avro_reader:
                    line_no += 1
                    yield {
                        record_field: self._to_output_value(
                            avro_format,
                            schema_field_name_to_type[record_field],  # type: ignore [index] # Any not subscriptable
                            record[record_field],  # type: ignore [index] # Any not subscriptable
                        )
                        for record_field, record_value in schema_field_name_to_type.items()
                    }
        except Exception as exc:
            raise RecordParseError(
                FileBasedSourceError.ERROR_PARSING_RECORD, filename=file.uri, lineno=line_no
            ) from exc

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ_BINARY

    @staticmethod
    def _to_output_value(
        avro_format: AvroFormat, record_type: Mapping[str, Any], record_value: Any
    ) -> Any:
        if isinstance(record_value, bytes):
            return record_value.decode()
        elif not isinstance(record_type, Mapping):
            if record_type == "double" and avro_format.double_as_string:
                return str(record_value)
            return record_value
        if record_type.get("logicalType") in ("decimal", "uuid"):
            return str(record_value)
        elif record_type.get("logicalType") == "date":
            return record_value.isoformat()
        elif record_type.get("logicalType") == "timestamp-millis":
            return record_value.isoformat(sep="T", timespec="milliseconds")
        elif record_type.get("logicalType") == "timestamp-micros":
            return record_value.isoformat(sep="T", timespec="microseconds")
        elif record_type.get("logicalType") == "local-timestamp-millis":
            return record_value.isoformat(sep="T", timespec="milliseconds")
        elif record_type.get("logicalType") == "local-timestamp-micros":
            return record_value.isoformat(sep="T", timespec="microseconds")
        else:
            return record_value
