#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config, Record


class PaginationStopCondition(ABC):
    @abstractmethod
    def is_met(self, response: requests.Response, last_records: List[Record]) -> bool:
        """
        Given a condition is met, the pagination will stop.
        Receives the same arguments as next_page_token

        :param response: the last response from the API
        :param last_records: the last records extracted
        """


class CursorStopCondition(PaginationStopCondition):
    def __init__(self, cursor: Cursor):
        self._cursor = cursor

    def is_met(self, response: requests.Response, last_records: List[Record]) -> bool:
        # We evaluate in reverse order because the assumption is that most of the APIs using data feed structure will return records in
        # descending order. In terms of performance/memory, we return the records lazily
        return any(not self._cursor.should_be_synced(record) for record in reversed(last_records))


class InterpolatedStopCondition(PaginationStopCondition):
    def __init__(self, condition: Union[InterpolatedBoolean, str], decoder: Decoder, parameters: Mapping[str, Any], config: Config):
        self._decoder = decoder or JsonDecoder(parameters={})
        self._config = config

        if isinstance(condition, str):
            self._condition = InterpolatedBoolean(condition=condition, parameters=parameters)
        else:
            self._condition = condition

    def is_met(self, response: requests.Response, last_records: List[Record]) -> bool:
        decoded_response = self._decoder.decode(response)

        # The default way that link is presented in requests.Response is a string of various links (last, next, etc). This
        # is not indexable or useful for parsing the cursor, so we replace it with the link dictionary from response.links
        headers = response.headers
        # Incompatible types in assignment (expression has type "dict[Any, Any]", target has type "str")  [assignment]
        headers["link"] = response.links  # type: ignore[assignment]

        return self._condition.eval(self._config, response=decoded_response, headers=response.headers, last_records=last_records)


class StopConditionPaginationStrategyDecorator(PaginationStrategy):
    def __init__(self, _delegate: PaginationStrategy, stop_condition: PaginationStopCondition):
        self._delegate = _delegate
        self._stop_condition = stop_condition

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Any]:
        if last_records and self._stop_condition.is_met(response, last_records):
            return None
        return self._delegate.next_page_token(response, last_records)

    def reset(self) -> None:
        self._delegate.reset()

    def get_page_size(self) -> Optional[int]:
        return self._delegate.get_page_size()

    @property
    def initial_token(self) -> Optional[Any]:
        return self._delegate.initial_token
