#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic.v1 import BaseModel, Field


class BlobFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Blob Format"
        description = "File-based sync."
        discriminator = "filetype"

    filetype: str = Field(
        "blob",
        const=True,
    )
