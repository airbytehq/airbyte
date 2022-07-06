#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from abc import abstractmethod
from typing import Any, List, Mapping, Optional

import requests


class PaginationStrategy:
    @abstractmethod
    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        pass
