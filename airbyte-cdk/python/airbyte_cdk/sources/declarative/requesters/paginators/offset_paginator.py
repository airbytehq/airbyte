#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.states.dict_state import DictState


class OffsetPaginator(Paginator):
    def __init__(self, page_size: int, state: Optional[DictState] = None, offset_key: str = "offset"):
        self._limit = page_size
        self._state = state or DictState()
        self._offsetKey = offset_key
        self._update_state_with_offset(0)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        print(f"len last_records: {last_records}")
        if len(last_records) < self._limit:
            return None
        offset = self._get_offset() + self._limit
        token_map = {self._offsetKey: offset}
        self._update_state_with_offset(offset)
        print(f"offset next page token: {token_map}")
        return token_map

    def _update_state_with_offset(self, offset):
        self._state.update_state(**{self._offsetKey: offset})

    def _get_offset(self):
        return self._state.get_state(self._offsetKey)

    def path(self):
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}
