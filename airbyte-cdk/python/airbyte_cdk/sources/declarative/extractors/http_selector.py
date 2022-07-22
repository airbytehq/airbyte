#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping

import requests
from airbyte_cdk.sources.declarative.types import Record


class HttpSelector(ABC):
    """
    Responsible for translating an HTTP response into a list of records by extracting records from the response and optionally filtering
    records based on a heuristic.
    """

    @abstractmethod
    def select_records(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> List[Record]:
        """
        Selects records from the response
        :param response: The response to select the records from
        :param stream_state: The stream state
        :param stream_slice: The stream slice
        :param next_page_token: The paginator token
        :return: List of Records selected from the response
        """
        pass
