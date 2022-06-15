#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.states.dict_state import DictState


class ConditionalPaginator:
    """
    A paginator that performs pagination by incrementing a page number and stops based on a provided stop condition.
    """

    def __init__(self, stop_condition_template: str, state: DictState, decoder: Decoder, config):
        self._stop_condition_template = InterpolatedBoolean(stop_condition_template)
        self._state: DictState = state
        self._decoder = decoder
        self._config = config

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        decoded_response = self._decoder.decode(response)
        headers = response.headers
        should_stop = self._stop_condition_template.eval(
            self._config, decoded_response=decoded_response, headers=headers, last_records=last_records
        )

        if should_stop:
            return None
        next_page = self._get_page() + 1
        self._update_page_state(next_page)
        return {"page": next_page}

    def _get_page(self):
        return self._state.get_state("page")

    def _update_page_state(self, page):
        self._state.update_state(**{"page": page})
