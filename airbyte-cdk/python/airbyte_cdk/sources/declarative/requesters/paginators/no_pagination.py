#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator


class NoPagination(Paginator):
    """
    Pagination implementation that never returns a next page.
    """

    def path(self) -> Optional[str]:
        return None

    def request_params(self) -> Mapping[str, Any]:
        return {}

    def request_headers(self) -> Mapping[str, str]:
        return {}

    def request_body_data(self) -> Union[Mapping[str, Any], str]:
        return {}

    def request_body_json(self) -> Mapping[str, Any]:
        return {}

    def request_kwargs(self) -> Mapping[str, Any]:
        # Never update kwargs
        return {}

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Mapping[str, Any]:
        return {}
