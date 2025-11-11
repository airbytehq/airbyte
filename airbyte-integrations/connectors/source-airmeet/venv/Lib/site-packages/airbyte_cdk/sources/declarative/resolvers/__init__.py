#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Mapping

from pydantic.v1 import BaseModel

from airbyte_cdk.sources.declarative.models import (
    ConfigComponentsResolver as ConfigComponentsResolverModel,
)
from airbyte_cdk.sources.declarative.models import (
    HttpComponentsResolver as HttpComponentsResolverModel,
)
from airbyte_cdk.sources.declarative.models import (
    ParametrizedComponentsResolver as ParametrizedComponentsResolverModel,
)
from airbyte_cdk.sources.declarative.resolvers.components_resolver import (
    ComponentMappingDefinition,
    ComponentsResolver,
    ResolvedComponentMappingDefinition,
)
from airbyte_cdk.sources.declarative.resolvers.config_components_resolver import (
    ConfigComponentsResolver,
    StreamConfig,
)
from airbyte_cdk.sources.declarative.resolvers.http_components_resolver import (
    HttpComponentsResolver,
)
from airbyte_cdk.sources.declarative.resolvers.parametrized_components_resolver import (
    ParametrizedComponentsResolver,
    StreamParametersDefinition,
)

COMPONENTS_RESOLVER_TYPE_MAPPING: Mapping[str, type[BaseModel]] = {
    "HttpComponentsResolver": HttpComponentsResolverModel,
    "ConfigComponentsResolver": ConfigComponentsResolverModel,
    "ParametrizedComponentsResolver": ParametrizedComponentsResolverModel,
}

__all__ = [
    "ComponentsResolver",
    "HttpComponentsResolver",
    "ComponentMappingDefinition",
    "ResolvedComponentMappingDefinition",
    "StreamConfig",
    "ConfigComponentsResolver",
    "COMPONENTS_RESOLVER_TYPE_MAPPING",
    "ParametrizedComponentsResolver",
    "StreamParametersDefinition",
]
