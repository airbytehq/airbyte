#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator


class NoPagination(Paginator):
    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        print(f"paginator: {len(last_records)}")
        if len(last_records) == 100:
            return {"starting_after": last_records[-1]["id"]}
        else:
            return None
