#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.config.parquet_format import ParquetFormat
from airbyte_cdk.sources.file_based.schema_helpers import type_mapping_to_jsonschema
from pydantic import BaseModel, Field, validator

PrimaryKeyType = Optional[Union[str, List[str]]]


VALID_FILE_TYPES = {"csv": CsvFormat, "parquet": ParquetFormat, "jsonl": JsonlFormat}


class FileBasedStreamConfig(BaseModel):
    name: str = Field(title="Name", description="The name of the stream.")
    file_type: str = Field(title="File Type", description="The data file type that is being extracted for a stream.")
    globs: Optional[List[str]] = Field(
        title="Globs",
        description='The pattern used to specify which files should be selected from the file system. For more information on glob pattern matching look <a href="https://en.wikipedia.org/wiki/Glob_(programming)">here</a>.',
    )
    validation_policy: str = Field(
        title="Validation Policy",
        description="The name of the validation policy that dictates sync behavior when a record does not adhere to the stream schema.",
    )
    input_schema: Optional[Union[str, Mapping[str, Any]]] = Field(
        title="Input Schema",
        description="The schema that will be used to validate records extracted from the file. This will override the stream schema that is auto-detected from incoming files.",
    )
    primary_key: PrimaryKeyType = Field(
        title="Primary Key", description="The column or columns (for a composite key) that serves as the unique identifier of a record."
    )
    days_to_sync_if_history_is_full: int = Field(
        title="Days To Sync If History Is Full",
        description="When the state history of the file store is full, syncs will only read files that were last modified in the provided day range.",
        default=3,
    )
    format: Optional[Mapping[str, Union[CsvFormat, ParquetFormat, JsonlFormat]]] = Field(
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

    @validator("format", pre=True)
    def transform_format(cls, v: Mapping[str, str]) -> Any:
        # The difference between legacy and new format is that the new format is a mapping of file type to format
        # This allows us to support multiple file types for a single stream
        if isinstance(v, Mapping):
            file_type = v.get("filetype", "")
            if file_type:
                return cls._transform_legacy_config(v, file_type)
            else:
                if len(v) > 1:
                    raise ValueError(
                        f"Format can only have one file type specified, got {v}"
                    )  # FIXME: remove this check when we support multiple file types for a single stream
                try:
                    return {key: VALID_FILE_TYPES[key.casefold()].parse_obj(val) for key, val in v.items()}
                except KeyError as e:
                    raise ValueError(f"Format filetype {e.args[0]} is not a supported file type")
        return v

    @classmethod
    def _transform_legacy_config(cls, legacy_config: Mapping[str, Any], file_type: str) -> Mapping[str, Any]:
        if file_type.casefold() not in VALID_FILE_TYPES:
            raise ValueError(f"Format filetype {file_type} is not a supported file type")
        if file_type.casefold() == "parquet":
            legacy_config = cls._transform_legacy_parquet_config(legacy_config)
        return {file_type: VALID_FILE_TYPES[file_type.casefold()].parse_obj({key: val for key, val in legacy_config.items()})}

    @classmethod
    def _transform_legacy_parquet_config(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        The legacy parquet parser converts decimal fields to numbers. This isn't desirable because it can lead to precision loss.
        To avoid introducing a breaking change with the new default, we will set decimal_as_float to True in the legacy configs.
        """
        if config.get("filetype") != "parquet":
            raise ValueError(
                f"Expected parquet format, got {config}. This is probably due to a CDK bug. Please reach out to the Airbyte team for support."
            )
        if config.get("decimal_as_float"):
            raise ValueError(
                "Received legacy parquet file form with 'decimal_as_float' set. This is unexpected. Please reach out to the Airbyte team for support."
            )
        return {**config, **{"decimal_as_float": True}}

    @validator("input_schema", pre=True)
    def transform_input_schema(cls, v: Optional[Union[str, Mapping[str, Any]]]) -> Optional[Mapping[str, Any]]:
        if v:
            schema = type_mapping_to_jsonschema(v)
            if not schema:
                raise ValueError(f"Unable to create JSON schema from input schema {v}")
            return schema
        return None
