#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator


class NoPagination(Paginator):
    def path(self) -> Optional[str]:
        return None

    def request_params(self) -> Mapping[str, Any]:
        return None

    def request_headers(self) -> Mapping[str, Any]:
        return None

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        return None

    def request_body_json(self) -> Optional[Mapping]:
        return None

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        return None
