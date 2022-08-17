#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config


class CursorPaginationStrategy(PaginationStrategy):
    """
    Pagination strategy that evaluates an interpolated string to define the next page token
    """

    def __init__(
        self,
        cursor_value: Union[InterpolatedString, str],
        config: Config,
        stop_condition: Optional[InterpolatedBoolean] = None,
        decoder: Optional[Decoder] = None,
        **options: Optional[Mapping[str, Any]],
    ):
        """
        :param cursor_value: template string evaluating to the cursor value
        :param config: connection config
        :param stop_condition: template string evaluating when to stop paginating
        :param decoder: decoder to decode the response
        :param options: Additional runtime parameters to be used for string interpolation
        """
        if isinstance(cursor_value, str):
            cursor_value = InterpolatedString.create(cursor_value, options=options)
        self._cursor_value = cursor_value
        self._config = config
        self._decoder = decoder or JsonDecoder()
        self._stop_condition = stop_condition

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self._decoder.decode(response)
        headers = response.headers
        if self._stop_condition:
            should_stop = self._stop_condition.eval(self._config, response=decoded_response, headers=headers, last_records=last_records)
            if should_stop:
                return None
        token = self._cursor_value.eval(config=self._config, last_records=last_records, response=decoded_response)
        return token if token else None
