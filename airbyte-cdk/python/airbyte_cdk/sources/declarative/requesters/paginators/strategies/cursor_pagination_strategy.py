#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config, Record

DECODED_RESPONSE_TYPE = Union[Mapping[str, Any], List[dict[str, Any]]]


@dataclass
class CursorPaginationStrategy(PaginationStrategy, ABC):
    """
    Abstract class for cursor pagination strategy

    Attributes:
        page_size (Optional[int]): the number of records to request
        decoder (Decoder): decoder to decode the response
    """

    page_size: Optional[int] = None
    decoder: Decoder = JsonDecoder(parameters={})

    @property
    def initial_token(self) -> Optional[Any]:
        return None

    @property
    def stop_condition(self) -> bool:
        return True

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)

        # The default way that link is presented in requests.Response is a string of various links (last, next, etc). This
        # is not indexable or useful for parsing the cursor, so we replace it with the link dictionary from response.links
        headers = response.headers
        headers["link"] = response.links  # type: ignore[assignment]

        if self.stop_condition:
            should_stop = self.stop(response=decoded_response, headers=headers, last_records=last_records)
            if should_stop:
                return None
        token = self.get_cursor_value(last_records=last_records, response=decoded_response, headers=headers)
        return token if token else None

    @abstractmethod
    def stop(self, response: DECODED_RESPONSE_TYPE, headers: Mapping[str, Any], last_records: List[Record]) -> bool:
        """
        Returns the value of whether to continue pagination or stop

        Attributes:
            response (Union[Mapping[str, Any], List]): Decoded response data
            headers (Mapping[str, Any]): Mapping of headers
            last_records (List[Mapping[str, Any]]): The list of the last records

        return: bool
        """

    @abstractmethod
    def get_cursor_value(self, response: DECODED_RESPONSE_TYPE, headers: Mapping[str, Any], last_records: List[Record]) -> Optional[str]:
        """
        Returns the string of actual cursor field as next_page_token value

        Attributes:
            response (Union[Mapping[str, Any], List]): Decoded response data
            headers (Mapping[str, Any]): Mapping of headers
            last_records (List[Mapping[str, Any]]): The list of the last records

        return: Optional[str]
        """

    def reset(self) -> None:
        # No state to reset
        pass

    def get_page_size(self) -> Optional[int]:
        return self.page_size


class LowCodeCursorPaginationStrategy(CursorPaginationStrategy):
    """
    Low code pagination strategy that evaluates an interpolated string to define the next page token

    Attributes:
        page_size (Optional[int]): the number of records to request
        cursor_value (Union[InterpolatedString, str]): template string evaluating to the cursor value
        config (Config): connection config
        stop_condition (Optional[Union[InterpolatedBoolean, str]]): template string evaluating when to stop paginating
        decoder (Decoder): decoder to decode the response
    """

    def __init__(
        self,
        parameters: Mapping[str, Any],
        config: Config,
        cursor_value: Union[InterpolatedString, str],
        stop_condition: Optional[Union[InterpolatedBoolean, str]] = None,
        page_size: Optional[int] = None,
        decoder: Decoder = JsonDecoder(parameters={}),
    ):
        self.cursor_value = (
            InterpolatedString.create(cursor_value, parameters=parameters) if isinstance(cursor_value, str) else cursor_value
        )
        self._stop_condition = (
            InterpolatedBoolean(condition=stop_condition, parameters=parameters) if isinstance(stop_condition, str) else stop_condition
        )
        self.config = config
        super().__init__(page_size=page_size, decoder=decoder)

    @property
    def stop_condition(self) -> bool:
        return self._stop_condition is not None

    def stop(self, response: DECODED_RESPONSE_TYPE, headers: Mapping[str, Any], last_records: List[Record]) -> bool:
        if not self._stop_condition:
            return False

        stop_value: bool = self._stop_condition.eval(self.config, response=response, headers=headers, last_records=last_records)
        return stop_value

    def get_cursor_value(self, response: DECODED_RESPONSE_TYPE, headers: Mapping[str, Any], last_records: List[Record]) -> Optional[str]:
        cursor_value = self.cursor_value.eval(config=self.config, response=response, headers=headers, last_records=last_records)
        return cursor_value or None
