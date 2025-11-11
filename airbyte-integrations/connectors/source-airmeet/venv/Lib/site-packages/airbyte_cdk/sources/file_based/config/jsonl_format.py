#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic.v1 import BaseModel, Field

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig


class JsonlFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Jsonl Format"
        discriminator = "filetype"

    filetype: str = Field(
        "jsonl",
        const=True,
    )
