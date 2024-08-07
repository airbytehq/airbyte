#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic.v1 import BaseModel, Field


class ExcelFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Excel Format"
        discriminator = "filetype"

    filetype: str = Field(
        "excel",
        const=True,
    )
