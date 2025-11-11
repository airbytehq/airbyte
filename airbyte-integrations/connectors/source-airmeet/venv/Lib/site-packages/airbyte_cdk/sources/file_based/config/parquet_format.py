#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pydantic.v1 import BaseModel, Field

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig


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
