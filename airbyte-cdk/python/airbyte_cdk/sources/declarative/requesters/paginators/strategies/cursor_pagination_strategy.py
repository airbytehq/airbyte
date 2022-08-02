#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class CursorPaginationStrategy(PaginationStrategy, JsonSchemaMixin):
    """
    Pagination strategy that evaluates an interpolated string to define the next page token

    Attributes:
        cursor_value (Union[InterpolatedString, str]): template string evaluating to the cursor value
        config (Config): connection config
        stop_condition (Optional[InterpolatedBoolean]): template string evaluating when to stop paginating
        decoder (Decoder): decoder to decode the response
        options (Optional[Mapping[str, Any]]): Additional runtime parameters to be used for string interpolation
    """

    cursor_value: Union[InterpolatedString, str]
    config: Config
    stop_condition: Optional[InterpolatedBoolean] = None
    decoder: Decoder = JsonDecoder()
    options: InitVar[Mapping[str, Any]] = None

    def __post_init__(self, options: Mapping[str, Any]):
        if isinstance(self.cursor_value, str):
            self.cursor_value = InterpolatedString.create(self.cursor_value, options=options or {})

    # def __init__(
    #     self,
    #     cursor_value: Union[InterpolatedString, str],
    #     config: Config,
    #     stop_condition: Optional[InterpolatedBoolean] = None,
    #     decoder: Optional[Decoder] = None,
    #     **options: Optional[Mapping[str, Any]],
    # ):
    #     """
    #     :param cursor_value: template string evaluating to the cursor value
    #     :param config: connection config
    #     :param stop_condition: template string evaluating when to stop paginating
    #     :param decoder: decoder to decode the response
    #     :param options: Additional runtime parameters to be used for string interpolation
    #     """
    #     if isinstance(cursor_value, str):
    #         cursor_value = InterpolatedString.create(cursor_value, options=options)
    #     self._cursor_value = cursor_value
    #     self._config = config
    #     self._decoder = decoder or JsonDecoder()
    #     self._stop_condition = stop_condition

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)
        headers = response.headers
        if self.stop_condition:
            should_stop = self.stop_condition.eval(self.config, response=decoded_response, headers=headers, last_records=last_records)
            if should_stop:
                return None
        token = self.cursor_value.eval(config=self.config, last_records=last_records, response=decoded_response)
        return token if token else None
