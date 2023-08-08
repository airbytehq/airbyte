#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field
from typing_extensions import Literal


class AvroFormat(BaseModel):
    class Config:
        title = "Avro Format"

    filetype: Literal["avro"] = "avro"

    # This option is not recommended, but necessary for backwards compatibility
    double_as_string: bool = Field(
        title="Convert Double Fields to Strings",
        description="Whether to convert double fields to strings. There is a loss of precision when converting decimals to floats, so this is recommended.",
        default=True,
    )
