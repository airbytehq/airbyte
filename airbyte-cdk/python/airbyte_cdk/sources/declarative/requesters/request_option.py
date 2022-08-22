#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from enum import Enum
from typing import Any, Mapping, Optional

from dataclasses_jsonschema import JsonSchemaMixin


class RequestOptionType(Enum):
    """
    Describes where to set a value on a request
    """

    request_parameter = "request_parameter"
    header = "header"
    path = "path"
    body_data = "body_data"
    body_json = "body_json"


@dataclass
class RequestOption(JsonSchemaMixin):
    """
    Describes an option to set on a request

    Attributes:
        inject_into (RequestOptionType): Describes where in the HTTP request to inject the parameter
        field_name (Optional[str]): Describes the name of the parameter to inject. None if option_type == path. Required otherwise.
    """

    inject_into: RequestOptionType
    options: InitVar[Mapping[str, Any]]
    field_name: Optional[str] = None

    def __post_init__(self, options: Mapping[str, Any]):
        if self.inject_into == RequestOptionType.path:
            if self.field_name is not None:
                raise ValueError(f"RequestOption with path cannot have a field name. Get {self.field_name}")
        elif self.field_name is None:
            raise ValueError(f"RequestOption expected field name for type {self.inject_into}")

    def is_path(self) -> bool:
        """Returns true if the parameter is the path to send the request to"""
        return self.inject_into == RequestOptionType.path
