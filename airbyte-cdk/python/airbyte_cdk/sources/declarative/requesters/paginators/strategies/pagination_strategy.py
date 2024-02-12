#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional

import requests
from airbyte_cdk.sources.declarative.types import Record


@dataclass
class PaginationStrategy:
    """
    Defines how to get the next page token
    """

    @property
    @abstractmethod
    def initial_token(self) -> Optional[Any]:
        """
        Return the initial value of the token
        """

    @abstractmethod
    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Any]:
        """
        :param response: response to process
        :param last_records: records extracted from the response
        :return: next page token. Returns None if there are no more pages to fetch
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the pagination's inner state
        """

    @abstractmethod
    def get_page_size(self) -> Optional[int]:
        """
        :return: page size: The number of records to fetch in a page. Returns None if unspecified
        """
