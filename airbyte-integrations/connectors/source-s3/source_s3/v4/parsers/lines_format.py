from pydantic.v1 import BaseModel, Field

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig


class LinesFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Line Format"
        discriminator = "filetype"

    filetype: str = Field(
        "lines",
        const=True,
    )

    unexpected_field_behavior: str = Field(
        title="Unexpected field behavior",
        default="infer",
        description="How fields outside of explicit_schema (if given) are treated. This determines what to do when encountering data that isn't defined in the schema.",
        enum=["ignore", "infer", "error"],
        order=0,
    )
    
    block_size: int = Field(
        default=0,
        description="The chunk size in bytes to process at a time in memory from each file. If your data is particularly wide and failing during schema detection, increasing this should solve it. Beware of raising this too high as you could hit OOM errors.",
        order=1,
    )