#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import codecs
from enum import Enum
from typing import Optional, Set

from pydantic import BaseModel, Field, validator
from typing_extensions import Literal


class InferenceType(Enum):
    NONE = "None"
    PRIMITIVE_TYPES_ONLY = "Primitive Types Only"


DEFAULT_TRUE_VALUES = ["y", "yes", "t", "true", "on", "1"]
DEFAULT_FALSE_VALUES = ["n", "no", "f", "false", "off", "0"]


class CsvFormat(BaseModel):
    class Config:
        title = "CSV Format"

    filetype: Literal["csv"] = "csv"
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
    null_values: Set[str] = Field(
        title="Null Values",
        default=[],
        description="A set of case-sensitive strings that should be interpreted as null values. For example, if the value 'NA' should be interpreted as null, enter 'NA' in this field.",
    )
    strings_can_be_null: bool = Field(
        title="Strings Can Be Null",
        default=True,
        description="Whether strings can be interpreted as null values. If true, strings that match the null_values set will be interpreted as null. If false, strings that match the null_values set will be interpreted as the string itself.",
    )
    skip_rows_before_header: int = Field(
        title="Skip Rows Before Header",
        default=0,
        description="The number of rows to skip before the header row. For example, if the header row is on the 3rd row, enter 2 in this field.",
    )
    skip_rows_after_header: int = Field(
        title="Skip Rows After Header", default=0, description="The number of rows to skip after the header row."
    )
    autogenerate_column_names: bool = Field(
        title="Autogenerate Column Names",
        default=False,
        description="Whether to autogenerate column names if column_names is empty. If true, column names will be of the form “f0”, “f1”… If false, column names will be read from the first CSV row after skip_rows_before_header.",
    )
    true_values: Set[str] = Field(
        title="True Values",
        default=DEFAULT_TRUE_VALUES,
        description="A set of case-sensitive strings that should be interpreted as true values.",
    )
    false_values: Set[str] = Field(
        title="False Values",
        default=DEFAULT_FALSE_VALUES,
        description="A set of case-sensitive strings that should be interpreted as false values.",
    )
    inference_type: InferenceType = Field(
        title="Inference Type",
        default=InferenceType.NONE,
        description="How to infer the types of the columns. If none, inference default to strings.",
        airbyte_hidden=True,
    )

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
        if v is not None and len(v) != 1:
            raise ValueError("escape_char should only be one character")
        return v

    @validator("encoding")
    def validate_encoding(cls, v: str) -> str:
        try:
            codecs.lookup(v)
        except LookupError:
            raise ValueError(f"invalid encoding format: {v}")
        return v
