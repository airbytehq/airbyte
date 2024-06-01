#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field
from typing import Literal


class AvroFormat(BaseModel):
    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config(OneOfOptionConfig):
        title = "Avro Format"
        discriminator = "filetype"

    filetype: Literal["avro"] = "avro"

    double_as_string: bool = Field(
        title="Convert Double Fields to Strings",
        description="Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers.",
        default=False,
    )
