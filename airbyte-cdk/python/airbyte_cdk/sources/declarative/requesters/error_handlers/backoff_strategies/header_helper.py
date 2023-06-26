#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import numbers
from re import Pattern
from typing import Optional

import requests


def get_numeric_value_from_header(response: requests.Response, header: str, regex: Optional[Pattern]) -> Optional[float]:
    """
    Extract a header value from the response as a float
    :param response: response the extract header value from
    :param header: Header to extract
    :param regex: optional regex to apply on the header to obtain the value
    :return: header value as float if it's a number. None otherwise
    """
    header_value = response.headers.get(header, None)
    if not header_value:
        return None
    if isinstance(header_value, str):
        if regex:
            match = regex.match(header_value)
            if match:
                header_value = match.group()
        return _as_float(header_value)
    elif isinstance(header_value, numbers.Number):
        return float(header_value)
    else:
        return None


def _as_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except ValueError:
        return None
