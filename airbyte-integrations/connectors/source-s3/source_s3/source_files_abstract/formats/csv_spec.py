#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
        default=None,
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
