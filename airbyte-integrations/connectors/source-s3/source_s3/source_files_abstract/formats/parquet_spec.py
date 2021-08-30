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

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# We need this in as a dummy for now so that format comes out correctly as a oneOf


class ParquetFormat(BaseModel):
    class Config:
        title = "parquet"

    class ParquetFiletype(str, Enum):
        parquet = "parquet"

    filetype: ParquetFiletype

    buffer_size: int = Field(
        default=0,
        description="perform read buffering when deserializing individual  column chunks. Otherwise IO calls are unbuffered.",
    )

    memory_map: bool = Field(
        default=False,
        description="If the source is a file path, use a memory map to read file, which can improve performance in some environments.",
    )

    columns: Optional[List[str]] = Field(
        default=None,
        description="If you only want to sync a subset of the columns from the file(s), add the columns you want here. Leave it empty to sync all columns.",
    )

    batch_size: int = Field(
        default=64 * 1024,  # 64K records
        description="Maximum number of records per batch. Batches may be smaller if there aren’t enough rows in the file.",
    )

    row_groups: Optional[List[int]] = Field(
        default=None,
        description="Only these row groups will be read from the file.",
    )

    use_threads: bool = Field(
        default=True,
        description="Perform multi-threaded column reads.",
    )
