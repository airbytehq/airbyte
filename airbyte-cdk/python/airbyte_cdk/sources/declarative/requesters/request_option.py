#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Optional


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

    def __init__(self, inject_into: RequestOptionType, field_name: Optional[str] = None):
        """
        :param inject_into: where to set the value
        :param field_name: field name to set. None if option_type == path. Required otherwise.
        """
        self._option_type = inject_into
        self._field_name = field_name
        if self._option_type == RequestOptionType.path:
            if self._field_name is not None:
                raise ValueError(f"RequestOption with path cannot have a field name. Get {field_name}")
        elif self._field_name is None:
            raise ValueError(f"RequestOption expected field name for type {self._option_type}")

    @property
    def inject_into(self) -> RequestOptionType:
        """Describes where in the HTTP request to inject the parameter"""
        return self._option_type

    @property
    def field_name(self) -> Optional[str]:
        """Describes the name of the parameter to inject"""
        return self._field_name

    def is_path(self) -> bool:
        """Returns true if the parameter is the path to send the request to"""
        return self._option_type == RequestOptionType.path
