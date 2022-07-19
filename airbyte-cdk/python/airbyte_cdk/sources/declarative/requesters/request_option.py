#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Optional, Union


class RequestOptionType(Enum):
    """
    Describes where to set a value on a request
    """

    request_parameter = "request_parameter"
    header = "header"
    path = "path"
    body_data = "body_data"
    body_json = "body_json"


class RequestOption:
    """
    Describes an option to set on a request
    """

    def __init__(self, pass_by: Union[RequestOptionType, str], field_name: Optional[str] = None):
        """
        :param pass_by: where to set the value
        :param field_name: field name to set. None if option_type == path. Required otherwise.
        """
        if isinstance(pass_by, str):
            pass_by = RequestOptionType[pass_by]
        self._option_type = pass_by
        self._field_name = field_name
        if self._option_type == RequestOptionType.path:
            if self._field_name is not None:
                raise ValueError(f"RequestOption with path cannot have a field name. Get {field_name}")
        elif self._field_name is None:
            raise ValueError(f"RequestOption expected field name for type {self._option_type}")

    @property
    def option_type(self) -> RequestOptionType:
        return self._option_type

    @property
    def field_name(self) -> Optional[RequestOptionType]:
        return self._field_name

    def is_path(self):
        return self._option_type == RequestOptionType.path
