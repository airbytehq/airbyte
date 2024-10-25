# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Literal

from airbyte_cdk import OneOfOptionConfig
from pydantic.v1 import BaseModel, Field


class BaseSyncConfig(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Sync file configuration"
        discriminator = "sync_type"

    sync_type: Literal["base"] = Field("base", const=True)
