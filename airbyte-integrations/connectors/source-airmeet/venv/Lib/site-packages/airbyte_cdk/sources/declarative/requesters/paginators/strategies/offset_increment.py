#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.decoders import (
    Decoder,
    JsonDecoder,
    PaginationDecoderDecorator,
)
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import (
    PaginationStrategy,
)
from airbyte_cdk.sources.types import Config, Record


@dataclass
class OffsetIncrement(PaginationStrategy):
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
          page_size: "{{ parameters['items_per_page'] }}"

    Attributes:
        page_size (InterpolatedString): the number of records to request
    """

    config: Config
    page_size: Optional[Union[str, int]]
    parameters: InitVar[Mapping[str, Any]]
    extractor: Optional[RecordExtractor]
    decoder: Decoder = field(
        default_factory=lambda: PaginationDecoderDecorator(decoder=JsonDecoder(parameters={}))
    )
    inject_on_first_request: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        page_size = str(self.page_size) if isinstance(self.page_size, int) else self.page_size
        if page_size:
            self._page_size: Optional[InterpolatedString] = InterpolatedString(
                page_size, parameters=parameters
            )
        else:
            self._page_size = None

    @property
    def initial_token(self) -> Optional[Any]:
        if self.inject_on_first_request:
            return 0
        return None

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any] = None,
    ) -> Optional[Any]:
        decoded_response = next(self.decoder.decode(response))

        if self.extractor:
            page_size_from_response = len(list(self.extractor.extract_records(response=response)))
            # The extractor could return 0 records which is valid, but evaluates to False. Our fallback in other
            # cases as the best effort option is to use the incoming last_page_size
            last_page_size = (
                page_size_from_response if page_size_from_response is not None else last_page_size
            )

        # Stop paginating when there are fewer records than the page size or the current page has no records
        if (
            self._page_size
            and last_page_size < self._page_size.eval(self.config, response=decoded_response)
        ) or last_page_size == 0:
            return None
        elif last_page_token_value is None:
            # If the OffsetIncrement strategy does not inject on the first request, the incoming last_page_token_value
            # will be None. For this case, we assume that None was the first page and progress to the next offset
            return 0 + last_page_size
        elif not isinstance(last_page_token_value, int):
            raise ValueError(
                f"Last page token value {last_page_token_value} for OffsetIncrement pagination strategy was not an integer"
            )
        else:
            return last_page_token_value + last_page_size

    def get_page_size(self) -> Optional[int]:
        if self._page_size:
            page_size = self._page_size.eval(self.config)
            if not isinstance(page_size, int):
                raise Exception(f"{page_size} is of type {type(page_size)}. Expected {int}")
            return page_size
        else:
            return None
