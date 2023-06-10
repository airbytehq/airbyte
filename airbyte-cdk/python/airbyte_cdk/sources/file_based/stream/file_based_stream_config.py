#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.file_based.remote_file import FileType
from airbyte_cdk.sources.file_based.schema_validation_policies import UserValidationPolicies
from pydantic import BaseModel


class FileBasedStreamConfig(BaseModel):
    name: str
    file_type: FileType
    globs: Optional[List[str]]
    validation_policy: UserValidationPolicies
    catalog_schema: Optional[ConfiguredAirbyteCatalog]
    input_schema: Optional[Mapping[str, Any]]
    primary_key: Optional[Any]
