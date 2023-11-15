#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field


class ParquetFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Parquet Format"
        discriminator = "filetype"

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

    skip_unprocessable_file_types: Optional[bool] = Field(
        default=True,
        title="Skip Unprocessable File Types",
        description="If true, skip files that cannot be parsed because of their file type and log a warning. If false, fail the sync. Corrupted files with valid file types will still result in a failed sync.",
        always_show=True,
    )
