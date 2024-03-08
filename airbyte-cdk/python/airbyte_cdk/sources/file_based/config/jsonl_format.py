#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field


class JsonlFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Jsonl Format"
        discriminator = "filetype"

    filetype: str = Field(
        "jsonl",
        const=True,
    )
