#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class Paginator(ABC, RequestOptionsProvider, JsonSchemaMixin):
    """
    Defines the token to use to fetch the next page of records from the API.

    If needed, the Paginator will set request options to be set on the HTTP request to fetch the next page of records.
    If the next_page_token is the path to the next page of records, then it should be accessed through the `path` method
    """

    @abstractmethod
    def reset(self):
        """
        Reset the pagination's inner state
        """

    @abstractmethod
    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        """
        Returns the next_page_token to use to fetch the next page of records.

        :param response: the response to process
        :param last_records: the records extracted from the response
        :return: A mapping {"next_page_token": <token>} for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
        pass

    @abstractmethod
    def path(self) -> Optional[str]:
        """
        Returns the URL path to hit to fetch the next page of records

        e.g: if you wanted to hit https://myapi.com/v1/some_entity then this will return "some_entity"

        :return: path to hit to fetch the next request. Returning None means the path is not defined by the next_page_token
        """
        pass
