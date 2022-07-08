#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import numbers
from re import Pattern
from typing import Optional

import requests


def get_numeric_value_from_header(response: requests.Response, header: str, regex: Optional[Pattern]) -> Optional[float]:
    header_value = response.headers.get(header, None)
    if not header_value:
        return None
    if isinstance(header_value, str):
        if regex:
            match = regex.match(header_value)
            if match:
                header_value = match[0]
        if header_value.isnumeric():
            return float(header_value)
    elif isinstance(header_value, numbers.Number):
        return float(header_value)
    else:
        return None
