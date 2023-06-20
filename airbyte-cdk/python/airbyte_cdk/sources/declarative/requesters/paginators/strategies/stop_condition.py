#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Optional

import requests
from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Record


class PaginationStopCondition(ABC):
    @abstractmethod
    def is_met(self, record: Record) -> bool:
        raise NotImplementedError()


class CursorStopCondition(PaginationStopCondition):
    def __init__(self, cursor: Cursor):
        self._cursor = cursor

    def is_met(self, record: Record) -> bool:
        return not self._cursor.should_be_synced(record)


class StopConditionPaginationStrategyDecorator(PaginationStrategy):
    def __init__(self, _delegate: PaginationStrategy, stop_condition: PaginationStopCondition):
        self._delegate = _delegate
        self._stop_condition = stop_condition

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Any]:
        if last_records and self._stop_condition.is_met(last_records[-1]):
            return None
        return self._delegate.next_page_token(response, last_records)

    def reset(self):
        self._delegate.reset()

    def get_page_size(self) -> Optional[int]:
        return self._delegate.get_page_size()
