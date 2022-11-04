from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class OffsetIncrementWorkaround(PaginationStrategy, JsonSchemaMixin):
    """
    Pagination strategy that returns the number of records reads so far and returns it as the next page token

    Attributes:
        page_size (int): the number of records to request
    """

    config: Config

    page_size: Union[InterpolatedString, str]
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._offset = 0
        self.page_size = InterpolatedString.create(self.page_size, options=options)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        if len(last_records) < self.page_size.eval(self.config):
            return None
        else:
            self._offset += len(last_records)
            return self._offset

    def reset(self):
        self._offset = 0

    def get_page_size(self) -> Optional[int]:
        return self.page_size.eval(self.config)
