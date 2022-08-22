#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from pydantic import BaseModel, Field


class ParquetFormat(BaseModel):
    'This connector utilises <a href="https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html" target="_blank">PyArrow (Apache Arrow)</a> for Parquet parsing.'

    class Config:
        title = "Parquet"

    filetype: str = Field("parquet", const=True)

    columns: Optional[List[str]] = Field(
        default=None,
        description="If you only want to sync a subset of the columns from the file(s), add the columns you want here as a comma-delimited"
        " list. Leave it empty to sync all columns.",
        title="Selected Columns",
        order=0,
    )
    batch_size: int = Field(
        title="Record batch size",
        order=1,
        default=64 * 1024,  # 64K records
        description="Maximum number of records per batch read from the input files. "
        "Batches may be smaller if there aren’t enough rows in the file. "
        "This option can help avoid out-of-memory errors if your data is particularly wide.",
    )
    buffer_size: int = Field(
        default=2,
        description="Perform read buffering when deserializing individual column chunks. "
        "By default every group column will be loaded fully to memory. "
        "This option can help avoid out-of-memory errors if your data is particularly wide.",
    )
