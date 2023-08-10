#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.file_based.types import StreamSchema


class AbstractSchemaValidationPolicy(ABC):
    name: str
    validate_schema_before_sync = False  # Whether to verify that records conform to the schema during the stream's availabilty check

    @abstractmethod
    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Optional[StreamSchema]) -> bool:
        """
        Return True if the record passes the user's validation policy.
        """
        raise NotImplementedError()
