#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from pydantic import BaseModel, Field


class JsonFormat(BaseModel):
    'This connector utilises <a href="https://pandas.pydata.org/docs/reference/api/pandas.io.json.read_json.html" target="_blank">Pandas</a> for JSON parsing.'

    class Config:
        title = "Json"

    filetype: str = Field(
        "json",
        const=True,
    )

    newlines_in_values: bool = Field(
        title="Allow newlines in values",
        default=False,
        description="Whether newline characters are allowed in JSON values. Turning this on may affect performance. Leave blank to default to False.",
        order=0,
    )
    unexpected_field_behavior: str = Field(
        title="Unexpected Json Fields",
        default="infer",
        description="How JSON fields outside of explicit_schema (if given) are treated.",
        order=1,
    )

    block_size: int = Field(
        default=10000,
        description="The chunk size in bytes to process at a time in memory from each file. If your data is particularly wide and failing during schema detection, increasing this should solve it. Beware of raising this too high as you could hit OOM errors.",
        order=2,
    )
