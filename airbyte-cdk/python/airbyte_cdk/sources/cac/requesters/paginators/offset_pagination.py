#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.cac.requesters.paginators.paginator import Paginator


class OffsetPagination(Paginator):
    def __init__(self, page_size: int, tag: str = "offset"):
        self._limit = page_size
        self._tag = tag
        self._offset = 0

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        if len(last_records) < self._limit:
            return None

        self._offset += self._limit
        return {self._tag: self._offset}
