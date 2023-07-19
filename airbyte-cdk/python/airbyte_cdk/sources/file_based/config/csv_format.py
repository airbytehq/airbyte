#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import codecs
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator
from typing_extensions import Literal


class QuotingBehavior(Enum):
    QUOTE_ALL = "Quote All"
    QUOTE_SPECIAL_CHARACTERS = "Quote Special Characters"
    QUOTE_NONNUMERIC = "Quote Non-numeric"
    QUOTE_NONE = "Quote None"


class CsvFormat(BaseModel):
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
