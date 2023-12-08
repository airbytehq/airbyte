#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections.abc import Mapping
from dataclasses import InitVar, dataclass
from typing import Any

from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader


@dataclass
class InlineSchemaLoader(SchemaLoader):
    """Describes a stream's schema"""

    schema: dict[str, Any]
    parameters: InitVar[Mapping[str, Any]]

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.schema
