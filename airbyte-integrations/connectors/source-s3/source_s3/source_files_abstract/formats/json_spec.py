#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from pydantic import BaseModel, Field


class JsonFormat(BaseModel):
    'This connector utilises <a href="https://pandas.pydata.org/docs/reference/api/pandas.io.json.read_json.html" target="_blank">Pandas</a> for JSON parsing.'

    class Config:
        title = "Json"

    filetype: str = Field(
        "json",
        const=True,
    )

    orient: str = Field(
        default="columns",
        description='The expected JSON string format. Details can be found in the <a href="https://pandas.pydata.org/docs/reference/api/pandas.read_json.html">Pandas documentation</a>',
        examples=["split", "records", "index", "columns", "values", "table"],
    )
    lines: bool = Field(default=True, description="Read the file as a json object per line.")

    chunk_size: int = Field(
        default=100,
        description="If lines is True, returns a JsonReader iterator to read batches of `chunk_size` lines instead of the whole file at once.",
    )

    compression: str = Field(
        default="infer",
        description='For on-the-fly decompression of on-disk data. If "infer", then use gzip, bz2, zip or xz if path_or_buf is a string ending in ".gz", ".bz2", ".zip", or "xz", respectively, and no decompression otherwise. If using "zip", the ZIP file must contain only one data file to be read in. Set to None for no decompression.',
        examples=[".gz", ".bz2", ".zip", "xz"],
    )

    encoding: str = Field(default="utf8", description="The encoding to use to decode py3 bytes.")

    nrows: Optional[int] = Field(
        default=None,
        description="The number of lines from the line-delimited jsonfile that has to be read. This can only be passed if lines=True. If this is None, all the rows will be returned.",
    )
