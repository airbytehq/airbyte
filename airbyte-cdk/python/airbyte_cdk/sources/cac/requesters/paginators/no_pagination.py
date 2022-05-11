#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping, Optional

import requests
from airbyte_cdk.sources.cac.requesters.paginators.paginator import Paginator


class NoPagination(Paginator):
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None
