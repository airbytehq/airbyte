#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field


class JsonlFormat(BaseModel):
    class Config:
        title = "Jsonl Format"

    filetype: str = Field(
        "jsonl",
        const=True,
    )
