#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class CursorPaginationStrategy(PaginationStrategy, ABC):
    """
    Pagination strategy that evaluates an interpolated string to define the next page token

    Attributes:
        page_size (Optional[int]): the number of records to request
        cursor_value (Union[InterpolatedString, str]): template string evaluating to the cursor value
        config (Config): connection config
        stop_condition (Optional[InterpolatedBoolean]): template string evaluating when to stop paginating
        decoder (Decoder): decoder to decode the response
    """

    page_size: Optional[int] = None
    decoder: Decoder = JsonDecoder(parameters={})

    @property
    def initial_token(self) -> Optional[Any]:
        return None

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)

        # The default way that link is presented in requests.Response is a string of various links (last, next, etc). This
        # is not indexable or useful for parsing the cursor, so we replace it with the link dictionary from response.links
        headers = response.headers
        headers["link"] = response.links

        if self.stop:
            should_stop = self.stop(response=decoded_response, headers=headers, last_records=last_records)
            if should_stop:
                return None
        token = self.get_cursor_value(last_records=last_records, response=decoded_response, headers=headers)
        return token if token else None

    def reset(self):
        # No state to reset
        pass

    def get_page_size(self) -> Optional[int]:
        return self.page_size

    @abstractmethod
    def stop(self, response, headers, last_records) -> bool:
        pass

    @abstractmethod
    def get_cursor_value(self, response, headers, last_records) -> str:
        pass


class LowCodeCursorPaginationStrategy(CursorPaginationStrategy):

    def __init__(self, cursor_value: str, decoder, page_size, config, parameters, stop_condition):
        if isinstance(cursor_value, str):
            self.cursor_value = InterpolatedString.create(cursor_value, parameters=parameters)
        else:
            self.cursor_value = cursor_value
        if isinstance(stop_condition, str):
            self.stop_condition = InterpolatedBoolean(condition=stop_condition, parameters=parameters)
        else:
            self.stop_condition = stop_condition
        super().__init__(page_size=page_size, decoder=decoder)
        self._config = config

    def stop(self, response, headers, last_records) -> bool:
        if self.stop_condition:
            return self.stop_condition.eval(response=response, headers=headers, last_records=last_records, config=self._config)
        else:
            return False

    def get_cursor_value(self, response, headers, last_records) -> str:
        return self.cursor_value.eval(response=response, headers=headers, last_records=last_records, config=self._config)
