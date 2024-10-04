# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from typing import Literal
from pydantic.v1 import Field
from airbyte_cdk.sources.file_based.config.clients_config.base_sync_config import BaseSyncConfig


class LocalSyncConfig(BaseSyncConfig):
    sync_type: Literal["local"] = Field("local", const=True)
