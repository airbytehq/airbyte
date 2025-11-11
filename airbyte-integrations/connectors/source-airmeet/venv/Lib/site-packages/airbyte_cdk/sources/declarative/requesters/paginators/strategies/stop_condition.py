#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Optional

import requests

from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import (
    PaginationStrategy,
)
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.types import Record


class PaginationStopCondition(ABC):
    @abstractmethod
    def is_met(self, record: Record) -> bool:
        """
        Given a condition is met, the pagination will stop

        :param record: a record used to evaluate the condition
        """
        raise NotImplementedError()


class CursorStopCondition(PaginationStopCondition):
    def __init__(
        self,
        cursor: Cursor,
    ):
        self._cursor = cursor

    def is_met(self, record: Record) -> bool:
        return not self._cursor.should_be_synced(record)


class StopConditionPaginationStrategyDecorator(PaginationStrategy):
    def __init__(self, _delegate: PaginationStrategy, stop_condition: PaginationStopCondition):
        self._delegate = _delegate
        self._stop_condition = stop_condition

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any] = None,
    ) -> Optional[Any]:
        # We evaluate in reverse order because the assumption is that most of the APIs using data feed structure
        # will return records in descending order. In terms of performance/memory, we return the records lazily
        if last_record and self._stop_condition.is_met(last_record):
            return None
        return self._delegate.next_page_token(
            response, last_page_size, last_record, last_page_token_value
        )

    def get_page_size(self) -> Optional[int]:
        return self._delegate.get_page_size()

    @property
    def initial_token(self) -> Optional[Any]:
        return self._delegate.initial_token
