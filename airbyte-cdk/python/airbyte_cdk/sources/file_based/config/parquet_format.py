#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Literal

from airbyte_cdk.utils.oneof_option_config import one_of_model_config
from pydantic import BaseModel, Field


class ParquetFormat(BaseModel):
    model_config = one_of_model_config(title="Parquet Format", description="Read data from Parquet files.", discriminator="filetype")
    filetype: Literal["parquet"] = "parquet"
    # This option is not recommended, but necessary for backwards compatibility
    decimal_as_float: bool = Field(
        title="Convert Decimal Fields to Floats",
        description="Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended.",
        default=False,
    )
