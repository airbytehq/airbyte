#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.types import Config


class NextPageUrlPaginator(Paginator):
    """
    A paginator wrapper that delegates to an inner paginator and removes the base url from the next_page_token to only return the path to the next page
    """

    def __init__(
        self,
        url_base: str = None,
        next_page_token_template: Optional[Mapping[str, str]] = None,
        config: Optional[Config] = None,
    ):
        """
        :param url_base: url base to remove from the token
        :param interpolated_paginator: optional paginator to delegate to
        :param next_page_token_template: optional mapping to delegate to if interpolated_paginator is None
        :param config: connection config
        """

        self._url_base = url_base
        self._interpolated_paginator = InterpolatedPaginator(next_page_token_template=next_page_token_template, config=config)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        next_page_token = self._interpolated_paginator.next_page_token(response, last_records)
        if next_page_token:
            return {k: v.replace(self._url_base, "") for k, v in next_page_token.items() if v}
        else:
            return None
