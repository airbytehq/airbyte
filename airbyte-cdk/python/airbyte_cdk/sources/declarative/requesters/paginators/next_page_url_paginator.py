#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.response import Response


class NextPageUrlPaginator(Paginator):
    def __init__(self, url_base: str, next_page_url: str, config=None, kwargs=None):
        if kwargs is None:
            kwargs = dict()

        self._url_base = url_base or kwargs.get("url_base")
        self._interpolated_paginator = InterpolatedPaginator({"next_page_url": next_page_url}, config)
        self._next_page_token = {}

    def get_headers(self) -> Mapping[str, Any]:
        return {}

    def get_request_parameters(self) -> Mapping[str, Any]:
        return {}

    def get_path(self) -> Optional[str]:
        return self._next_page_token.get("next_page_url")

    def next_page_token(self, response: Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        self._next_page_token = self._interpolated_paginator.next_page_token(response, last_records)
        if self._next_page_token:
            self._next_page_token = {k: v.replace(self._url_base, "") for k, v in self._next_page_token.items() if v}
        return self._next_page_token
