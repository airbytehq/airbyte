#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping

from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class SchemaLoader(JsonSchemaMixin):
    """Describes a stream's schema"""

    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        """Returns a mapping describing the stream's schema"""
        pass
