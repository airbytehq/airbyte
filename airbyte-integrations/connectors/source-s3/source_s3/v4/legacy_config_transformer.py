#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from typing import Any, List, Mapping, Optional, Union

from source_s3.source import SourceS3Spec
from source_s3.source_files_abstract.formats.avro_spec import AvroFormat
from source_s3.source_files_abstract.formats.csv_spec import CsvFormat
from source_s3.source_files_abstract.formats.jsonl_spec import JsonlFormat
from source_s3.source_files_abstract.formats.parquet_spec import ParquetFormat

SECONDS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MICROS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class LegacyConfigTransformer:
    """
    Class that takes in S3 source configs in the legacy format and transforms them into
    configs that can be used by the new S3 source built with the file-based CDK.
    """

    @classmethod
    def convert(cls, legacy_config: SourceS3Spec) -> Mapping[str, Any]:
        transformed_config = {
            "bucket": legacy_config.provider.bucket,
            "streams": [
                {
                    "name": legacy_config.dataset,
                    "file_type": legacy_config.format.filetype,
                    "globs": cls._create_globs(legacy_config.path_pattern),
                    "legacy_prefix": legacy_config.provider.path_prefix,
                    "validation_policy": "Emit Record",
                }
            ],
        }

        if legacy_config.provider.start_date:
            transformed_config["start_date"] = cls._transform_seconds_to_micros(legacy_config.provider.start_date)
        if legacy_config.provider.aws_access_key_id:
            transformed_config["aws_access_key_id"] = legacy_config.provider.aws_access_key_id
        if legacy_config.provider.aws_secret_access_key:
            transformed_config["aws_secret_access_key"] = legacy_config.provider.aws_secret_access_key
        if legacy_config.provider.endpoint:
            transformed_config["endpoint"] = legacy_config.provider.endpoint
        if legacy_config.user_schema and legacy_config.user_schema != "{}":
            transformed_config["streams"][0]["input_schema"] = legacy_config.user_schema
        if legacy_config.format:
            transformed_config["streams"][0]["format"] = cls._transform_file_format(legacy_config.format)

        return transformed_config

    @classmethod
    def _create_globs(cls, path_pattern: str) -> List[str]:
        if "|" in path_pattern:
            return path_pattern.split("|")
        else:
            return [path_pattern]

    @classmethod
    def _transform_seconds_to_micros(cls, datetime_str: str) -> str:
        try:
            parsed_datetime = datetime.strptime(datetime_str, SECONDS_FORMAT)
            return parsed_datetime.strftime(MICROS_FORMAT)
        except ValueError as e:
            raise ValueError("Timestamp could not be parsed when transforming legacy connector config") from e

    @classmethod
    def _transform_file_format(cls, format_options: Union[CsvFormat, ParquetFormat, AvroFormat, JsonlFormat]) -> Mapping[str, Any]:
        if isinstance(format_options, AvroFormat):
            return {"filetype": "avro"}
        elif isinstance(format_options, CsvFormat):
            additional_reader_options = cls.parse_config_options_str("additional_reader_options", format_options.additional_reader_options)
            advanced_options = cls.parse_config_options_str("advanced_options", format_options.advanced_options)

            csv_options = {
                "filetype": "csv",
                "delimiter": format_options.delimiter,
                "quote_char": format_options.quote_char,
                "double_quote": format_options.double_quote,
                "null_values": ["", "null", "NULL", "N/A", "NA", "NaN", "None"],
                "true_values": ["y", "yes", "t", "true", "on", "1"],
                "false_values": ["n", "no", "f", "false", "off", "0"],
                "inference_type": "Primitive Types Only" if format_options.infer_datatypes else "None",
                "strings_can_be_null": additional_reader_options.get("strings_can_be_null", False),
            }

            if format_options.escape_char:
                csv_options["escape_char"] = format_options.escape_char
            if format_options.encoding:
                csv_options["encoding"] = format_options.encoding
            if "skip_rows" in advanced_options:
                csv_options["skip_rows_before_header"] = advanced_options["skip_rows"]
            if "skip_rows_after_names" in advanced_options:
                csv_options["skip_rows_after_header"] = advanced_options["skip_rows_after_names"]
            if "autogenerate_column_names" in advanced_options:
                csv_options["autogenerate_column_names"] = advanced_options["autogenerate_column_names"]
            return csv_options

        elif isinstance(format_options, JsonlFormat):
            return {"filetype": "jsonl"}
        elif isinstance(format_options, ParquetFormat):
            return {"filetype": "parquet", "decimal_as_float": True}
        else:
            # This should never happen because it would fail schema validation
            raise ValueError(f"Format filetype {format_options} is not a supported file type")

    @classmethod
    def parse_config_options_str(cls, options_field: str, options_value: Optional[str]) -> Mapping[str, Any]:
        options_str = options_value or "{}"
        try:
            return json.loads(options_str)
        except json.JSONDecodeError as error:
            raise ValueError(f"Malformed {options_field} config json: {error}. Please ensure that it is a valid JSON.")
