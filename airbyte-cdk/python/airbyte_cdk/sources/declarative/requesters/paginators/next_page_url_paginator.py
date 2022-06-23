#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator


class NextPageUrlPaginator(Paginator):
    def __init__(self, url_base: str = None, interpolated_paginator: InterpolatedPaginator = None, kwargs=None):
        if kwargs is None:
            kwargs = dict()
        self._url_base = url_base or kwargs.get("url_base")
        self._interpolated_paginator = interpolated_paginator or kwargs.get("interpolated_paginator")

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        next_page_token = self._interpolated_paginator.next_page_token(response, last_records)
        if next_page_token:
            return {k: v.replace(self._url_base, "") for k, v in next_page_token.items() if v}
        else:
            return None
