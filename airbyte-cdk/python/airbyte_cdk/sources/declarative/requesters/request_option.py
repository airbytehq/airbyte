#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin


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
    """

    """
    :param option_type: where to set the value
    :param field_name: field name to set. None if option_type == path. Required otherwise.
    """

    option_type: Union[RequestOptionType, str]
    field_name: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.option_type, str):
            self.option_type = RequestOptionType[self.option_type]
        self.option_type = self.option_type
        self.field_name = self.field_name
        if self.option_type == RequestOptionType.path:
            if self.field_name is not None:
                raise ValueError(f"RequestOption with path cannot have a field name. Get {self.field_name}")
        elif self.field_name is None:
            raise ValueError(f"RequestOption expected field name for type {self.option_type}")
