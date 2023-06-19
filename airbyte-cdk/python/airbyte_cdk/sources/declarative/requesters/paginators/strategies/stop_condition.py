#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy


class StopConditionPaginationStrategyDecorator(PaginationStrategy):
    def __init__(self, _delegate, stop_condition):
        self._delegate = _delegate
        self._stop_condition = stop_condition

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        if self.stop_condition.is_met(last_records[-1]):
            return None
        return self._delegate.next_page_token(response, last_records)

    def reset(self):
        self._delegate.reset()

    def get_page_size(self) -> Optional[int]:
        return self._delegate.get_page_size()


class PaginationStopCondition(ABC):
    @abstractmethod
    def is_met(self, last_record: Mapping[str, Any]) -> bool:
        raise NotImplementedError()


class CursorStopCondition(PaginationStopCondition):
    def __init__(self, cursor: Cursor):
        self._cursor = cursor

    def is_met(self, last_record: Mapping[str, Any]) -> bool:
        return not self._cursor.should_be_synced_based_on_initial_state(last_record)
