#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config


class CursorPaginationStrategy:
    # TODO: rename to something with URL!
    def __init__(self, cursor_value, config: Config):
        self._cursor_value = cursor_value
        self._config = config

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        next_page = {"next_page_token": InterpolatedString(self._cursor_value).eval(config=self._config, decoded_response=response.json())}
        self._token = next_page
        return self._token
