#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import codecs
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Union

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from pydantic import BaseModel, root_validator, validator

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
    validation_policy: Union[str, Any]
    validation_policies: Dict[str, Any]
    catalog_schema: Optional[ConfiguredAirbyteCatalog]
    input_schema: Optional[Dict[str, Any]]
    primary_key: PrimaryKeyType
    max_history_size: Optional[int]
    days_to_sync_if_history_is_full: Optional[int]
    format: Optional[Mapping[str, CsvFormat]]  # this will eventually be a Union once we have more than one format type

    @validator("format", pre=True)
    def transform_format(cls, v):
        if isinstance(v, Mapping):
            file_type = v.get("filetype", "")
            if file_type.casefold() not in VALID_FILE_TYPES:
                raise ValueError(f"Format filetype {file_type} is not a supported file type")
            return {file_type: {key: val for key, val in v.items()}}
        return v

    @root_validator
    def set_validation_policy(cls, values):
        validation_policy_key = values.get("validation_policy")
        validation_policies = values.get("validation_policies")

        if validation_policy_key not in validation_policies:
            raise ValueError(f"validation_policy must be one of {list(validation_policies.keys())}")

        values["validation_policy"] = validation_policies[validation_policy_key]

        return values
