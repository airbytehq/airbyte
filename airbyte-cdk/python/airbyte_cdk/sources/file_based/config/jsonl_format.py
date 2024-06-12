#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Literal

from airbyte_cdk.utils.oneof_option_config import one_of_model_config
from pydantic import BaseModel


class JsonlFormat(BaseModel):
    model_config = one_of_model_config(title="Jsonl Format", description="Read data from JSONL files.", discriminator="filetype")
    filetype: Literal["jsonl"] = "jsonl"
