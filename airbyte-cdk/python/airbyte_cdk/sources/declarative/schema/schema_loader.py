#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping


class SchemaLoader(ABC):
    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        pass
