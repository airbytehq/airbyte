#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from enum import Enum
from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


class RequestOptionType(Enum):
    """
    Describes where to set a value on a request
    """

    request_parameter = "request_parameter"
    header = "header"
    body_data = "body_data"
    body_json = "body_json"


@dataclass
class RequestOption:
    """
    Describes an option to set on a request

    Attributes:
        field_name (str): Describes the name of the parameter to inject
        inject_into (RequestOptionType): Describes where in the HTTP request to inject the parameter
    """

    field_name: Union[InterpolatedString, str]
    inject_into: RequestOptionType
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.field_name = InterpolatedString.create(self.field_name, parameters=parameters)
