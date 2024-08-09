#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from enum import Enum
from typing import Any, Callable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RequestOption as RequestOptionModel
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.types import Config
from pydantic import BaseModel


class RequestOptionType(Enum):
    """
    Describes where to set a value on a request
    """

    request_parameter = "request_parameter"
    header = "header"
    body_data = "body_data"
    body_json = "body_json"


@dataclass
class RequestOption(ComponentConstructor):
    """
    Describes an option to set on a request

    Attributes:
        field_name (str): Describes the name of the parameter to inject
        inject_into (RequestOptionType): Describes where in the HTTP request to inject the parameter
    """

    field_name: Union[InterpolatedString, str]
    inject_into: RequestOptionType
    parameters: InitVar[Mapping[str, Any]]

    @classmethod
    def resolve_dependencies(
        cls,
        model: RequestOptionModel,
        config: Config,
        dependency_constructor: Callable[[BaseModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        inject_into = RequestOptionType(model.inject_into.value)
        return {"field_name": model.field_name, "inject_into": inject_into, "parameters": {}}

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.field_name = InterpolatedString.create(self.field_name, parameters=parameters)
