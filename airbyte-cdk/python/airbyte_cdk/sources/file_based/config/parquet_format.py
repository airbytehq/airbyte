#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Literal

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field


class ParquetFormat(BaseModel):
    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config(OneOfOptionConfig):
        title = "Parquet Format"
        discriminator = "filetype"

    filetype: Literal["parquet"] = "parquet"
    # This option is not recommended, but necessary for backwards compatibility
    decimal_as_float: bool = Field(
        title="Convert Decimal Fields to Floats",
        description="Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended.",
        default=False,
    )
