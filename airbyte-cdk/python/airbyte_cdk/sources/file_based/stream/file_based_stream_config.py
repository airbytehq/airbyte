#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.file_based.schema_validation_policies import UserValidationPolicies
from pydantic import BaseModel

PrimaryKeyType = Optional[Union[str, List[str], List[List[str]]]]


class FileBasedStreamConfig(BaseModel):
    name: str
    file_type: str
    globs: Optional[List[str]]
    validation_policy: UserValidationPolicies
    catalog_schema: Optional[ConfiguredAirbyteCatalog]
    input_schema: Optional[Mapping[str, Any]]
    primary_key: PrimaryKeyType
