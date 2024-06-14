#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.sources.file_based.config.avro_format import AvroFormat
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.config.parquet_format import ParquetFormat
from airbyte_cdk.sources.file_based.config.unstructured_format import UnstructuredFormat
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, FileBasedSourceError
from airbyte_cdk.sources.file_based.schema_helpers import type_mapping_to_jsonschema
from pydantic.v1 import BaseModel, Field, validator

PrimaryKeyType = Optional[Union[str, List[str]]]


class ValidationPolicy(Enum):
    emit_record = "Emit Record"
    skip_record = "Skip Record"
    wait_for_discover = "Wait for Discover"


class FileBasedStreamConfig(BaseModel):
    name: str = Field(title="Name", description="The name of the stream.")
    globs: Optional[List[str]] = Field(
        default=["**"],
        title="Globs",
        description='The pattern used to specify which files should be selected from the file system. For more information on glob pattern matching look <a href="https://en.wikipedia.org/wiki/Glob_(programming)">here</a>.',
        order=1,
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
        title="Primary Key",
        description="The column or columns (for a composite key) that serves as the unique identifier of a record. If empty, the primary key will default to the parser's default primary key.",
        airbyte_hidden=True,  # Users can create/modify primary keys in the connection configuration so we shouldn't duplicate it here.
    )
    days_to_sync_if_history_is_full: int = Field(
        title="Days To Sync If History Is Full",
        description="When the state history of the file store is full, syncs will only read files that were last modified in the provided day range.",
        default=3,
    )
    format: Union[AvroFormat, CsvFormat, JsonlFormat, ParquetFormat, UnstructuredFormat] = Field(
        title="Format",
        description="The configuration options that are used to alter how to read incoming files that deviate from the standard formatting.",
    )
    schemaless: bool = Field(
        title="Schemaless",
        description="When enabled, syncs will not validate or structure records against the stream's schema.",
        default=False,
    )

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
