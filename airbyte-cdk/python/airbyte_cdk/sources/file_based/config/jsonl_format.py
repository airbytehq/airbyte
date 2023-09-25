#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel
from typing_extensions import Literal


class JsonlFormat(BaseModel):
    class Config:
        title = "Jsonl Format"

    filetype: Literal["jsonl"] = "jsonl"
