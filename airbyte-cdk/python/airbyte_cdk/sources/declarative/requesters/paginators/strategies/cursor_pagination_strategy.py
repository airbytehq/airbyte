#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Dict, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config, Record


@dataclass
class CursorPaginationStrategy(PaginationStrategy):
    """
    Pagination strategy that evaluates an interpolated string to define the next page token

    Attributes:
        page_size (Optional[int]): the number of records to request
        cursor_value (Union[InterpolatedString, str]): template string evaluating to the cursor value
        config (Config): connection config
        stop_condition (Optional[InterpolatedBoolean]): template string evaluating when to stop paginating
        decoder (Decoder): decoder to decode the response
    """

    cursor_value: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    page_size: Optional[int] = None
    stop_condition: Optional[Union[InterpolatedBoolean, str]] = None
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if isinstance(self.cursor_value, str):
            self._cursor_value = InterpolatedString.create(self.cursor_value, parameters=parameters)
        else:
            self._cursor_value = self.cursor_value
        if isinstance(self.stop_condition, str):
            self._stop_condition = InterpolatedBoolean(condition=self.stop_condition, parameters=parameters)
        else:
            self._stop_condition = self.stop_condition  # type: ignore # the type has been checked

    @property
    def initial_token(self) -> Optional[Any]:
        return None

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)

        # The default way that link is presented in requests.Response is a string of various links (last, next, etc). This
        # is not indexable or useful for parsing the cursor, so we replace it with the link dictionary from response.links
        headers: Dict[str, Any] = dict(response.headers)
        headers["link"] = response.links

        last_record = last_records[-1] if last_records else None

        if self._stop_condition:
            should_stop = self._stop_condition.eval(
                self.config,
                response=decoded_response,
                headers=headers,
                last_records=last_records,
                last_record=last_record,
                last_page_size=len(last_records),
            )
            if should_stop:
                return None
        token = self._cursor_value.eval(
            config=self.config,
            last_records=last_records,
            response=decoded_response,
            headers=headers,
            last_record=last_record,
            last_page_size=len(last_records),
        )
        return token if token else None

    def reset(self) -> None:
        # No state to reset
        pass

    def get_page_size(self) -> Optional[int]:
        return self.page_size
