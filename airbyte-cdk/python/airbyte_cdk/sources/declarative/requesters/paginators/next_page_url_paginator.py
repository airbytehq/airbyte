#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator


class NextPageUrlPaginator(Paginator):
    def __init__(
        self,
        url_base: str = None,
        interpolated_paginator: InterpolatedPaginator = None,
        next_page_token_template=None,
        kwargs=None,
        config=None,
    ):
        if next_page_token_template and interpolated_paginator:
            raise ValueError(
                f"Only one of next_page_token_template and interpolated_paginator is expected. Got {next_page_token_template} and {interpolated_paginator}"
            )
        if kwargs is None:
            kwargs = dict()
        self._url_base = url_base or kwargs.get("url_base")
        self._interpolated_paginator = (
            interpolated_paginator
            or kwargs.get("interpolated_paginator")
            or InterpolatedPaginator(next_page_token_template=next_page_token_template, config=config)
        )

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        next_page_token = self._interpolated_paginator.next_page_token(response, last_records)
        if next_page_token:
            return {k: v.replace(self._url_base, "") for k, v in next_page_token.items() if v}
        else:
            return None
