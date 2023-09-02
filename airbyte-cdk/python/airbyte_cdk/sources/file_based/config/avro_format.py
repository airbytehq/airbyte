#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field
from typing_extensions import Literal


class AvroFormat(BaseModel):
    class Config:
        title = "Avro Format"

    filetype: Literal["avro"] = "avro"

    double_as_string: bool = Field(
        title="Convert Double Fields to Strings",
        description="Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers.",
        default=False,
    )
