#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import codecs
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from pydantic import BaseModel, root_validator, validator

PrimaryKeyType = Optional[Union[str, List[str], List[List[str]]]]


class CsvFormat(BaseModel):
    filetype: str
    delimiter: str = ","
    quote_char: str = '"'
    escape_char: Optional[str]
    encoding: Optional[str] = "utf8"
    double_quote: bool
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
    catalog_schema: Optional[ConfiguredAirbyteCatalog]
    input_schema: Optional[Mapping[str, Any]]
    primary_key: PrimaryKeyType
    max_history_size: Optional[int]
    days_to_sync_if_history_is_full: Optional[int]
    format: Optional[CsvFormat]  # this will eventually be a Union once we have more than one format type

    @root_validator(pre=True)
    def validate_filetype(cls, values):
        # In the existing S3 configs, we specify file_type in two places. Ideally it should only be set at the
        # top-level of the config, but while we have it in two places we should emit an error if there is a mismatch
        config_format = values.get("format", {})
        if config_format:
            format_file_type = config_format.get("filetype")
            file_type = values.get("file_type")
            if file_type != format_file_type:
                raise ValueError(f"type mismatch between config file_type {file_type} and format filetype {format_file_type}")
        return values
