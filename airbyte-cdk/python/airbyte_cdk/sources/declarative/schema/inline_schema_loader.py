#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Dict, Mapping, Callable, Optional

from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.declarative.models.declarative_component_schema import InlineSchemaLoader as InlineSchemaLoaderModel
from airbyte_cdk.sources.types import Config

from pydantic import BaseModel


@dataclass
class InlineSchemaLoader(SchemaLoader, ComponentConstructor):
    """Describes a stream's schema"""

    schema: Dict[str, Any]
    parameters: InitVar[Mapping[str, Any]]


    @classmethod
    def resolve_dependencies(
        cls,
        model: InlineSchemaLoaderModel,
        config: Config,
        dependency_constructor: Callable[[BaseModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return {"schema":model.schema_ or {}, "parameters": {}}

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.schema
