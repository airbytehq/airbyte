#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import codecs
from enum import Enum
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from pydantic import BaseModel, validator

PrimaryKeyType = Optional[Union[str, List[str], List[List[str]]]]


class QuotingBehavior(Enum):
    QUOTE_ALL = "Quote All"
    QUOTE_SPECIAL_CHARACTERS = "Quote Special Characters"
    QUOTE_NONNUMERIC = "Quote Non-numeric"
    QUOTE_NONE = "Quote None"


class ParquetFormat(BaseModel):
    # Legacy S3 source converted decimal columns to floats, which is not ideal because it loses precision.
    # We default to keeping decimals as strings, but allow users to opt into the legacy behavior.
    decimal_as_float: bool = False


class JsonlFormat(BaseModel):
    pass


class CsvFormat(BaseModel):
    delimiter: str = ","
    quote_char: str = '"'
    escape_char: Optional[str]
    encoding: Optional[str] = "utf8"
    double_quote: bool
    quoting_behavior: QuotingBehavior = QuotingBehavior.QUOTE_SPECIAL_CHARACTERS
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


VALID_FILE_TYPES = {"csv": CsvFormat, "parquet": ParquetFormat, "jsonl": JsonlFormat}


class FileBasedStreamConfig(BaseModel):
    name: str
    file_type: str
    globs: Optional[List[str]]
    validation_policy: Any
    catalog_schema: Optional[ConfiguredAirbyteCatalog]
    input_schema: Optional[Mapping[str, Any]]
    primary_key: PrimaryKeyType
    max_history_size: Optional[int]
    days_to_sync_if_history_is_full: Optional[int]
    format: Optional[Mapping[str, Union[CsvFormat, ParquetFormat, JsonlFormat]]]
    schemaless: bool = False

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
                # legacy case
                if file_type.casefold() not in VALID_FILE_TYPES:
                    raise ValueError(f"Format filetype {file_type} is not a supported file type")
                ret = {file_type: VALID_FILE_TYPES[file_type.casefold()].parse_obj({key: val for key, val in v.items()})}
                return ret
            else:
                try:
                    return {key: VALID_FILE_TYPES[key.casefold()].parse_obj(val) for key, val in v.items()}
                except KeyError as e:
                    raise ValueError(f"Format filetype {e.args[0]} is not a supported file type")
        return v
