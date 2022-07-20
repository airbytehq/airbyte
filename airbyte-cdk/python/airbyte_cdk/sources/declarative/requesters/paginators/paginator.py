#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional

import requests


class Paginator(ABC):
    @abstractmethod
    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        """

        :param response: the response to process
        :param last_records: the records extracted from the response
        :return: A mapping {"next_page_token": <token>} for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
        pass

    @abstractmethod
    def path(self) -> Optional[str]:
        """
        :return: path to hit to fetch the next request. Returning None means the path does not need to be updated
        """
        pass

    @abstractmethod
    def request_params(self) -> Mapping[str, Any]:
        """

        :return: the request parameters to set to fetch the next page
        """
        pass

    @abstractmethod
    def request_headers(self) -> Mapping[str, str]:
        """

        :return: the request headers to set to fetch the next page
        """
        pass

    @abstractmethod
    def request_body_data(self) -> Mapping[str, Any]:
        """

        :return: the request body data to set to fetch the next page
        """
        pass

    @abstractmethod
    def request_body_json(self) -> Mapping[str, Any]:
        """

        :return: the request body to set (as a json object) to fetch the next page
        """
        pass
