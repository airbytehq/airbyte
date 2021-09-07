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

from typing import List, Optional

from pydantic import BaseModel, Field


class ParquetFormat(BaseModel):
    'This connector utilises <a href="https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html" target="_blank">PyArrow (Apache Arrow)</a> for Parquet parsing.'

    class Config:
        title = "parquet"

    filetype: str = Field(Config.title, const=True)

    buffer_size: int = Field(
        default=0,
        description="Perform read buffering when deserializing individual column chunks. By default every group column will be loaded fully to memory. This option can help to optimize a work with memory if your data is particularly wide or failing during detection of OOM errors.",
    )

    columns: Optional[List[str]] = Field(
        default=None,
        description="If you only want to sync a subset of the columns from the file(s), add the columns you want here. Leave it empty to sync all columns.",
    )

    batch_size: int = Field(
        default=64 * 1024,  # 64K records
        description="Maximum number of records per batch. Batches may be smaller if there aren’t enough rows in the file. This option can help to optimize a work with memory if your data is particularly wide or failing during detection of OOM errors.",
    )
