#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Literal

from airbyte_cdk.utils.oneof_option_config import one_of_model_config
from pydantic import BaseModel, Field


class AvroFormat(BaseModel):
    model_config = one_of_model_config(title="Avro Format", description="Read data from Avro files.", discriminator="filetype")

    filetype: Literal["avro"] = "avro"

    double_as_string: bool = Field(
        title="Convert Double Fields to Strings",
        description="Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers.",
        default=False,
    )
