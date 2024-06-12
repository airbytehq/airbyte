#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Literal

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel


class JsonlFormat(BaseModel):
    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config(OneOfOptionConfig):
        title = "Jsonl Format"
        discriminator = "filetype"

    filetype: Literal["jsonl"] = "jsonl"
