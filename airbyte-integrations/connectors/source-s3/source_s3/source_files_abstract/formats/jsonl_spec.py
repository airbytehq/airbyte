#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from enum import Enum

from pydantic import BaseModel, Field


class UnexpectedFieldBehaviorEnum(str, Enum):
    ignore = "ignore"
    infer = "infer"
    error = "error"


class JsonlFormat(BaseModel):
    'This connector uses <a href="https://arrow.apache.org/docs/python/json.html" target="_blank">PyArrow</a> for JSON Lines (jsonl) file parsing.'

    class Config:
        title = "Jsonl"

    filetype: str = Field(
        "jsonl",
        const=True,
    )

    newlines_in_values: bool = Field(
        title="Allow newlines in values",
        default=False,
        description="Whether newline characters are allowed in JSON values. Turning this on may affect performance. Leave blank to default to False.",
        order=0,
    )

    unexpected_field_behavior: UnexpectedFieldBehaviorEnum = Field(
        title="Unexpected field behavior",
        default="infer",
        description='How JSON fields outside of explicit_schema (if given) are treated. Check <a href="https://arrow.apache.org/docs/python/generated/pyarrow.json.ParseOptions.html" target="_blank">PyArrow documentation</a> for details',
        examples=["ignore", "infer", "error"],
        order=1,
    )
    # Block size set to 0 as default value to disable this feature for most not-experienced users
    block_size: int = Field(
        default=0,
        description="The chunk size in bytes to process at a time in memory from each file. If your data is particularly wide and failing during schema detection, increasing this should solve it. Beware of raising this too high as you could hit OOM errors.",
        order=2,
    )
