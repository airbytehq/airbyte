#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from enum import Enum
from typing import Any, Mapping


class AbstractSchemaValidationPolicy(Enum):
    @abstractmethod
    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
        """
        Return True if the record passes the user's validation policy.
        """
        ...
