#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class CursorPaginationStrategy(PaginationStrategy, JsonSchemaMixin):
    """
    Pagination strategy that evaluates an interpolated string to define the next page token

    Attributes:
        cursor_value (Union[InterpolatedString, str]): template string evaluating to the cursor value
        config (Config): connection config
        stop_condition (Optional[InterpolatedBoolean]): template string evaluating when to stop paginating
        decoder (Decoder): decoder to decode the response
    """

    cursor_value: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    stop_condition: Optional[Union[InterpolatedBoolean, str]] = None
    decoder: Decoder = JsonDecoder(options={})

    def __post_init__(self, options: Mapping[str, Any]):
        if isinstance(self.cursor_value, str):
            self.cursor_value = InterpolatedString.create(self.cursor_value, options=options)
        if isinstance(self.stop_condition, str):
            self.stop_condition = InterpolatedBoolean(condition=self.stop_condition, options=options)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)

        # The default way that link is presented in requests.Response is a string of various links (last, next, etc). This
        # is not indexable or useful for parsing the cursor, so we replace it with the link dictionary from response.links
        headers = response.headers
        headers["link"] = response.links

        if self.stop_condition:
            should_stop = self.stop_condition.eval(self.config, response=decoded_response, headers=headers, last_records=last_records)
            if should_stop:
                return None
        token = self.cursor_value.eval(config=self.config, last_records=last_records, response=decoded_response, headers=headers)
        return token if token else None

    def reset(self):
        # No state to reset
        pass
