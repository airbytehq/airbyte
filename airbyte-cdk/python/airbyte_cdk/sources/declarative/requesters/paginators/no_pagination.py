#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.response import Response


class NoPagination(Paginator):
    def next_page_token(self, response: Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        if len(last_records) >= 100:
            return {"starting_after": last_records[-1]["id"]}
        return None
