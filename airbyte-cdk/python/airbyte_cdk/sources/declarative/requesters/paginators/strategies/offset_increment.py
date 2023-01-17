#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class OffsetIncrement(PaginationStrategy, JsonSchemaMixin):
    """
    Pagination strategy that returns the number of records reads so far and returns it as the next page token
    Examples:
        # page_size to be a constant integer value
        pagination_strategy:
          type: OffsetIncrement
          page_size: 2

        # page_size to be a constant string value
        pagination_strategy:
          type: OffsetIncrement
          page_size: "2"

        # page_size to be an interpolated string value
        pagination_strategy:
          type: OffsetIncrement
          page_size: "{{ options['items_per_page'] }}"

    Attributes:
        page_size (InterpolatedString): the number of records to request
    """

    config: Config
    page_size: Union[str, int]
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._offset = 0
        page_size = str(self.page_size) if isinstance(self.page_size, int) else self.page_size
        self._page_size = InterpolatedString(page_size, options=options)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        if len(last_records) < self._page_size.eval(self.config):
            return None
        else:
            self._offset += len(last_records)
            return self._offset

    def reset(self):
        self._offset = 0

    def get_page_size(self) -> Optional[int]:
        page_size = self._page_size.eval(self.config)
        if not isinstance(page_size, int):
            raise Exception(f"{page_size} is of type {type(page_size)}. Expected {int}")
        return page_size
