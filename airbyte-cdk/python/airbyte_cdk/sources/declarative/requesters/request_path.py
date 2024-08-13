#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Callable, Mapping, Optional

from airbyte_cdk.sources.declarative.models.declarative_component_schema import RequestPath as RequestPathModel
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.types import Config


@dataclass
class RequestPath(ComponentConstructor[RequestPathModel, RequestPathModel]):
    """
    Describes that a component value should be inserted into the path
    """

    parameters: InitVar[Mapping[str, Any]]

    @classmethod
    def resolve_dependencies(
        cls,
        model: RequestPathModel,
        config: Config,
        dependency_constructor: Callable[[RequestPathModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return {"parameters": {}}
