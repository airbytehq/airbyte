#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Any, List, Mapping, Optional, Type, Union

from airbyte_cdk.sources.file_based.config.avro_format import AvroFormat
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.config.parquet_format import ParquetFormat
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, FileBasedSourceError
from airbyte_cdk.sources.file_based.schema_helpers import type_mapping_to_jsonschema
from pydantic import BaseModel, Field, validator

PrimaryKeyType = Optional[Union[str, List[str]]]


VALID_FILE_TYPES: Mapping[str, Type[BaseModel]] = {"avro": AvroFormat, "csv": CsvFormat, "jsonl": JsonlFormat, "parquet": ParquetFormat}


class ValidationPolicy(Enum):
    emit_record = "Emit Record"
    skip_record = "Skip Record"
    wait_for_discover = "Wait for Discover"


class FileBasedStreamConfig(BaseModel):
    name: str = Field(title="Name", description="The name of the stream.")
    file_type: str = Field(title="File Type", description="The data file type that is being extracted for a stream.")
    globs: Optional[List[str]] = Field(
        title="Globs",
        description='The pattern used to specify which files should be selected from the file system. For more information on glob pattern matching look <a href="https://en.wikipedia.org/wiki/Glob_(programming)">here</a>.',
    )
    legacy_prefix: Optional[str] = Field(
        title="Legacy Prefix",
        description="The path prefix configured in v3 versions of the S3 connector. This option is deprecated in favor of a single glob.",
        airbyte_hidden=True,
    )
    validation_policy: ValidationPolicy = Field(
        title="Validation Policy",
        description="The name of the validation policy that dictates sync behavior when a record does not adhere to the stream schema.",
        default=ValidationPolicy.emit_record,
    )
    input_schema: Optional[str] = Field(
        title="Input Schema",
        description="The schema that will be used to validate records extracted from the file. This will override the stream schema that is auto-detected from incoming files.",
    )
    primary_key: Optional[str] = Field(
        title="Primary Key", description="The column or columns (for a composite key) that serves as the unique identifier of a record."
    )
    days_to_sync_if_history_is_full: int = Field(
        title="Days To Sync If History Is Full",
        description="When the state history of the file store is full, syncs will only read files that were last modified in the provided day range.",
        default=3,
    )
    format: Optional[Union[AvroFormat, CsvFormat, JsonlFormat, ParquetFormat]] = Field(
        title="Format",
        description="The configuration options that are used to alter how to read incoming files that deviate from the standard formatting.",
    )
    schemaless: bool = Field(
        title="Schemaless",
        description="When enabled, syncs will not validate or structure records against the stream's schema.",
        default=False,
    )

    @validator("file_type", pre=True)
    def validate_file_type(cls, v: str) -> str:
        if v not in VALID_FILE_TYPES:
            raise ValueError(f"Format filetype {v} is not a supported file type")
        return v

    @classmethod
    def _transform_legacy_config(cls, legacy_config: Mapping[str, Any], file_type: str) -> Mapping[str, Any]:
        if file_type.casefold() not in VALID_FILE_TYPES:
            raise ValueError(f"Format filetype {file_type} is not a supported file type")
        if file_type.casefold() == "parquet" or file_type.casefold() == "avro":
            legacy_config = cls._transform_legacy_parquet_or_avro_config(legacy_config)
        return {file_type: VALID_FILE_TYPES[file_type.casefold()].parse_obj({key: val for key, val in legacy_config.items()})}

    @classmethod
    def _transform_legacy_parquet_or_avro_config(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        The legacy parquet parser converts decimal fields to numbers. This isn't desirable because it can lead to precision loss.
        To avoid introducing a breaking change with the new default, we will set decimal_as_float to True in the legacy configs.
        """
        filetype = config.get("filetype")
        if filetype != "parquet" and filetype != "avro":
            raise ValueError(
                f"Expected {filetype} format, got {config}. This is probably due to a CDK bug. Please reach out to the Airbyte team for support."
            )
        if config.get("decimal_as_float"):
            raise ValueError(
                f"Received legacy {filetype} file form with 'decimal_as_float' set. This is unexpected. Please reach out to the Airbyte team for support."
            )
        return {**config, **{"decimal_as_float": True}}

    @validator("input_schema", pre=True)
    def validate_input_schema(cls, v: Optional[str]) -> Optional[str]:
        if v:
            if type_mapping_to_jsonschema(v):
                return v
            else:
                raise ConfigValidationError(FileBasedSourceError.ERROR_PARSING_USER_PROVIDED_SCHEMA)
        return None

    def get_input_schema(self) -> Optional[Mapping[str, Any]]:
        """
        User defined input_schema is defined as a string in the config. This method takes the string representation
        and converts it into a Mapping[str, Any] which is used by file-based CDK components.
        """
        if self.input_schema:
            schema = type_mapping_to_jsonschema(self.input_schema)
            if not schema:
                raise ValueError(f"Unable to create JSON schema from input schema {self.input_schema}")
            return schema
        return None
