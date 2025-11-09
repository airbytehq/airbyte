from enum import Enum

from pydantic.v1 import BaseModel, Field


class UnexpectedFieldBehaviorEnum(str, Enum):
    ignore = "ignore"
    infer = "infer"
    error = "error"


class LinesFormat(BaseModel):
    class Config:
        title = "Lines"
    filetype: str = Field(
        "lines",
        const=True,
    )

    unexpected_field_behavior: UnexpectedFieldBehaviorEnum = Field(
        title="Unexpected field behavior",
        default="infer",
        description="How lines outside of explicit_schema (if given) are treated. This determines what to do when encountering lines that aren't defined in the schema.",
        examples=["ignore", "infer", "error"],
        order=0,
    )
    
    # Block size set to 0 as default value to disable this feature for most not-experienced users
    block_size: int = Field(
        default=0,
        description="The chunk size in bytes to process at a time in memory from each file. If your data is particularly wide and failing during schema detection, increasing this should solve it. Beware of raising this too high as you could hit OOM errors.",
        order=1,
    )