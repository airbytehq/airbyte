#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass
class SchemaLoader:
    """Describes a stream's schema"""

    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        """Returns a mapping describing the stream's schema"""
        pass
