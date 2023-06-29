#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from pydantic import BaseModel

PrimaryKeyType = Optional[Union[str, List[str], List[List[str]]]]


class FileBasedStreamConfig(BaseModel):
    name: str
    file_type: str
    globs: Optional[List[str]]
    validation_policy: str
    catalog_schema: Optional[ConfiguredAirbyteCatalog]
    input_schema: Optional[Mapping[str, Any]]
    primary_key: PrimaryKeyType
    max_history_size: Optional[int]
    days_to_sync_if_history_is_full: Optional[int]
