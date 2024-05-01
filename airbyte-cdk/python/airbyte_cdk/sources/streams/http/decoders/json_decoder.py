#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, Union

import requests

from .decoder import Decoder


class JsonDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], List]:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {}

    def validate_response(self, response: requests.Response) -> None:
        try:
            response.json()
        except requests.exceptions.JSONDecodeError:
            raise
