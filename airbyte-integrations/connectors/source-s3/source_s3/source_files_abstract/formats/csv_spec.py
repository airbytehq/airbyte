#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from pydantic import BaseModel, Field


class CsvFormat(BaseModel):
    'This connector utilises <a href="https: // arrow.apache.org/docs/python/generated/pyarrow.csv.open_csv.html" target="_blank">PyArrow (Apache Arrow)</a> for CSV parsing.'

    class Config:
        title = "csv"

    filetype: str = Field(
        Config.title,
        const=True,
    )

    delimiter: str = Field(
        default=",",
        min_length=1,
        description="The character delimiting individual cells in the CSV data. This may only be a 1-character string.",
    )
    quote_char: str = Field(
        default='"', description="The character used optionally for quoting CSV values. To disallow quoting, make this field blank."
    )
    escape_char: Optional[str] = Field(
        default=None,
        description="The character used optionally for escaping special characters. To disallow escaping, leave this field blank.",
    )
    encoding: Optional[str] = Field(
        default="utf8",
        description='The character encoding of the CSV data. Leave blank to default to <strong>UTF-8</strong>. See <a href="https://docs.python.org/3/library/codecs.html#standard-encodings" target="_blank">list of python encodings</a> for allowable options.',
    )
    double_quote: bool = Field(default=True, description="Whether two quotes in a quoted CSV value denote a single quote in the data.")
    newlines_in_values: bool = Field(
        default=False,
        description="Whether newline characters are allowed in CSV values. Turning this on may affect performance. Leave blank to default to False.",
    )
    block_size: int = Field(
        default=10000,
        description="The chunk size in bytes to process at a time in memory from each file. If your data is particularly wide and failing during schema detection, increasing this should solve it. Beware of raising this too high as you could hit OOM errors.",
    )
    additional_reader_options: str = Field(
        default="{}",
        description='Optionally add a valid JSON string here to provide additional options to the csv reader. Mappings must correspond to options <a href="https://arrow.apache.org/docs/python/generated/pyarrow.csv.ConvertOptions.html#pyarrow.csv.ConvertOptions" target="_blank">detailed here</a>. \'column_types\' is used internally to handle schema so overriding that would likely cause problems.',
        examples=[
            '{"timestamp_parsers": ["%m/%d/%Y %H:%M", "%Y/%m/%d %H:%M"], "strings_can_be_null": true, "null_values": ["NA", "NULL"]}'
        ],
    )
    advanced_options: str = Field(
        default="{}",
        description="Optionally add a valid JSON string here to provide additional <a href=\"https://arrow.apache.org/docs/python/generated/pyarrow.csv.ReadOptions.html#pyarrow.csv.ReadOptions\" target=\"_blank\">Pyarrow ReadOptions</a>. Specify 'column_names' here if your CSV doesn't have header, or if you want to use custom column names. 'block_size' and 'encoding' are already used above, specify them again here will override the values above.",
        examples=['{"column_names": ["column1", "column2"]}'],
    )
    infer_datatypes: Optional[bool] = Field(
        default=True,
        description="Configures whether a scheme for the source should be inferred from the current data or not."
        "If set to false and a custom schema is set, then the custom_schema is used"
        "If a custom schema is not set, and this is set to false, then all fields will be read as strings",
    )
