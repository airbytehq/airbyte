#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field


class ParquetFormat(BaseModel):
    class Config:
        title = "Parquet Format"

    filetype: str = Field(
        "parquet",
        const=True,
    )
    # This option is not recommended, but necessary for backwards compatibility
    decimal_as_float: bool = Field(
        title="Convert Decimal Fields to Floats",
        description="Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended.",
        default=False,
    )
