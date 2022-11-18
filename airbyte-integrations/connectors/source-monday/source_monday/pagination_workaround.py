from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class PageIncrementWorkaround(PaginationStrategy, JsonSchemaMixin):
    """
    Pagination strategy that returns the number of pages reads so far and returns it as the next page token

    Attributes:
        page_size Optional[InterpolatedString]: the number of records to request
    """

    config: Config

    page_size: Optional[Union[InterpolatedString, str]]
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._page = 1
        self._page_size = None

        self.page_size = InterpolatedString.create(self.page_size, options=options)

    def _eval_page_size(self, possible_record_len: int):
        if self._page_size:
            return self._page_size
        page_size = self.page_size.eval(self.config)
        if page_size:
            self._page_size = page_size
        else:
            self._page_size = possible_record_len
        return self._page_size

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        page_size = self._eval_page_size(len(last_records))
        if not page_size:
            return None
        if len(last_records) < page_size:
            return None
        self._page += 1
        return self._page

    def reset(self):
        self._page = 1

    def get_page_size(self) -> Optional[int]:
        return self.page_size.eval(self.config)
