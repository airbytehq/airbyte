#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import codecs
from enum import Enum
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.sources.file_based.schema_helpers import type_mapping_to_jsonschema
from pydantic import BaseModel, validator

PrimaryKeyType = Optional[Union[str, List[str], List[List[str]]]]

VALID_FILE_TYPES = {"avro", "csv", "jsonl", "parquet"}


class QuotingBehavior(Enum):
    QUOTE_ALL = "Quote All"
    QUOTE_SPECIAL_CHARACTERS = "Quote Special Characters"
    QUOTE_NONNUMERIC = "Quote Non-numeric"
    QUOTE_NONE = "Quote None"


class CsvFormat(BaseModel):
    delimiter: str = ","
    quote_char: str = '"'
    escape_char: Optional[str]
    encoding: Optional[str] = "utf8"
    double_quote: bool
    quoting_behavior: Optional[QuotingBehavior] = QuotingBehavior.QUOTE_SPECIAL_CHARACTERS
    # Noting that the existing S3 connector had a config option newlines_in_values. This was only supported by pyarrow and not
    # the Python csv package. It has a little adoption, but long term we should ideally phase this out because of the drawbacks
    # of using pyarrow

    @validator("delimiter")
    def validate_delimiter(cls, v):
        if len(v) != 1:
            raise ValueError("delimiter should only be one character")
        if v in {"\r", "\n"}:
            raise ValueError(f"delimiter cannot be {v}")
        return v

    @validator("quote_char")
    def validate_quote_char(cls, v):
        if len(v) != 1:
            raise ValueError("quote_char should only be one character")
        return v

    @validator("escape_char")
    def validate_escape_char(cls, v):
        if len(v) != 1:
            raise ValueError("escape_char should only be one character")
        return v

    @validator("encoding")
    def validate_encoding(cls, v):
        try:
            codecs.lookup(v)
        except LookupError:
            raise ValueError(f"invalid encoding format: {v}")
        return v


class FileBasedStreamConfig(BaseModel):
    name: str
    file_type: str
    globs: Optional[List[str]]
    validation_policy: str
    input_schema: Optional[Union[str, Mapping[str, Any]]]
    primary_key: PrimaryKeyType
    days_to_sync_if_history_is_full: int = 3
    format: Optional[Mapping[str, CsvFormat]]  # this will eventually be a Union once we have more than one format type
    schemaless: bool = False

    @validator("file_type", pre=True)
    def validate_file_type(cls, v):
        if v not in VALID_FILE_TYPES:
            raise ValueError(f"Format filetype {v} is not a supported file type")
        return v

    @validator("format", pre=True)
    def transform_format(cls, v):
        if isinstance(v, Mapping):
            file_type = v.get("filetype", "")
            if file_type:
                if file_type.casefold() not in VALID_FILE_TYPES:
                    raise ValueError(f"Format filetype {file_type} is not a supported file type")
                return {file_type: {key: val for key, val in v.items()}}
        return v

    @validator("input_schema", pre=True)
    def transform_input_schema(cls, v):
        if v:
            return type_mapping_to_jsonschema(v)
