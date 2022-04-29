#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from pydantic import BaseModel, Field


class AvroFormat(BaseModel):
    class Config:
        title = "avro"

    filetype: str = Field(
        Config.title,
        const=True,
    )
