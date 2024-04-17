#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import urllib.parse as urlparse
from dataclasses import InitVar, dataclass
from typing import Any, Dict, List, Mapping, Optional, Union
from urllib.parse import parse_qsl

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config, Record


@dataclass
class UrlPaginationStrategy(PaginationStrategy):
    """
    Custom component for cases when there is no information in the response body to match the current cursor position.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    cursor_field_name: Union[InterpolatedString, str]
    page_size: Optional[int] = None
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if isinstance(self.cursor_field_name, str):
            self._cursor_field_name = InterpolatedString.create(self.cursor_field_name, parameters=parameters)
        else:
            self._cursor_field_name = self.cursor_field_name

    @property
    def initial_token(self) -> Optional[Any]:
        return None

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)

        # The default way that link is presented in requests.Response is a string of various links (last, next, etc). This
        # is not indexable or useful for parsing the cursor, so we replace it with the link dictionary from response.links
        headers: Dict[str, Any] = dict(response.headers)
        headers["link"] = response.links

        last_record = last_records[-1] if last_records else None

        if len(last_records) == self.page_size:
            query_params = dict(parse_qsl(urlparse.urlparse(response.url).query))
            cursor_field_name = self._cursor_field_name.eval(
                config=self.config,
                last_records=last_records,
                response=decoded_response,
                headers=headers,
                last_record=last_record,
                last_page_size=len(last_records),
            )
            startAt = int(query_params.get(cursor_field_name, 0)) + self.page_size
            return startAt

    def reset(self) -> None:
        # No state to reset
        pass

    def get_page_size(self) -> Optional[int]:
        return self.page_size
