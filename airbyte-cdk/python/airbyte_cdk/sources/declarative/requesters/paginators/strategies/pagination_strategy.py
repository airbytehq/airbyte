#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

import requests
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class PaginationStrategy(JsonSchemaMixin):
    """
    Defines how to get the next page token
    """

    @abstractmethod
    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        """
        :param response: response to process
        :param last_records: records extracted from the response
        :return: next page token. Returns None if there are no more pages to fetch
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the pagination's inner state
        """
