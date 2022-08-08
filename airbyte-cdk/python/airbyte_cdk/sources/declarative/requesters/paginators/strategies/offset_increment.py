#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class OffsetIncrement(PaginationStrategy, JsonSchemaMixin):
    """
    Pagination strategy that returns the number of records reads so far and returns it as the next page token

    Attributes:
        page_size (int): the number of records to request
    """

    page_size: int
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._offset = 0

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        if len(last_records) < self.page_size:
            return None
        else:
            self._offset += len(last_records)
            return self._offset

    def reset(self):
        self._offset = 0
