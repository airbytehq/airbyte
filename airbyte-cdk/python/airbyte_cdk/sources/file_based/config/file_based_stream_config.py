#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import codecs
from enum import Enum
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.sources.file_based.schema_helpers import type_mapping_to_jsonschema
from pydantic import BaseModel, Field, validator

PrimaryKeyType = Optional[Union[str, List[str]]]

VALID_FILE_TYPES = {"avro", "csv", "jsonl", "parquet"}


class QuotingBehavior(Enum):
    QUOTE_ALL = "Quote All"
    QUOTE_SPECIAL_CHARACTERS = "Quote Special Characters"
    QUOTE_NONNUMERIC = "Quote Non-numeric"
    QUOTE_NONE = "Quote None"


class CsvFormat(BaseModel):
    delimiter: str = Field(
        title="Delimiter",
        description="The character delimiting individual cells in the CSV data. This may only be a 1-character string. For tab-delimited data enter '\\t'.",
        default=",",
    )
    quote_char: str = Field(
        title="Quote Character",
        default='"',
        description="The character used for quoting CSV values. To disallow quoting, make this field blank.",
    )
    escape_char: Optional[str] = Field(
        title="Escape Character",
        default=None,
        description="The character used for escaping special characters. To disallow escaping, leave this field blank.",
    )
    encoding: Optional[str] = Field(
        default="utf8",
        description='The character encoding of the CSV data. Leave blank to default to <strong>UTF8</strong>. See <a href="https://docs.python.org/3/library/codecs.html#standard-encodings" target="_blank">list of python encodings</a> for allowable options.',
    )
    double_quote: bool = Field(
        title="Double Quote", default=True, description="Whether two quotes in a quoted CSV value denote a single quote in the data."
    )
    quoting_behavior: QuotingBehavior = Field(
        title="Quoting Behavior",
        default=QuotingBehavior.QUOTE_SPECIAL_CHARACTERS,
        description="The quoting behavior determines when a value in a row should have quote marks added around it. For example, if Quote Non-numeric is specified, while reading, quotes are expected for row values that do not contain numbers. Or for Quote All, every row value will be expecting quotes.",
    )
    # Noting that the existing S3 connector had a config option newlines_in_values. This was only supported by pyarrow and not
    # the Python csv package. It has a little adoption, but long term we should ideally phase this out because of the drawbacks
    # of using pyarrow

    @validator("delimiter")
    def validate_delimiter(cls, v: str) -> str:
        if len(v) != 1:
            raise ValueError("delimiter should only be one character")
        if v in {"\r", "\n"}:
            raise ValueError(f"delimiter cannot be {v}")
        return v

    @validator("quote_char")
    def validate_quote_char(cls, v: str) -> str:
        if len(v) != 1:
            raise ValueError("quote_char should only be one character")
        return v

    @validator("escape_char")
    def validate_escape_char(cls, v: str) -> str:
        if len(v) != 1:
            raise ValueError("escape_char should only be one character")
        return v

    @validator("encoding")
    def validate_encoding(cls, v: str) -> str:
        try:
            codecs.lookup(v)
        except LookupError:
            raise ValueError(f"invalid encoding format: {v}")
        return v


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
    format: Optional[Mapping[str, CsvFormat]] = Field(
        title="Format",
        description="The configuration options that are used to alter how to read incoming files that deviate from the standard formatting.",
    )  # this will eventually be a Union once we have more than one format type
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
        if isinstance(v, Mapping):
            file_type = v.get("filetype", "")
            if file_type:
                if file_type.casefold() not in VALID_FILE_TYPES:
                    raise ValueError(f"Format filetype {file_type} is not a supported file type")
                return {file_type: {key: val for key, val in v.items()}}
        return v

    @validator("input_schema", pre=True)
    def transform_input_schema(cls, v: Optional[Union[str, Mapping[str, Any]]]) -> Optional[Mapping[str, Any]]:
        if v:
            schema = type_mapping_to_jsonschema(v)
            if not schema:
                raise ValueError(f"Unable to create JSON schema from input schema {v}")
            return schema
        return None
