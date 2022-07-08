#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config


class InterpolatedPaginationStrategy(PaginationStrategy):
    def __init__(self, template_string: Union[InterpolatedString, str], decoder: Decoder, config: Config):
        if isinstance(template_string, str):
            template_string = InterpolatedString(template_string)
        self._template_string = template_string
        self._decoder = decoder
        self._config = config

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        token = self._template_string.eval(self._config, decoded_response=self._decoder.decode(response), last_records=last_records)
        return token if token else None
