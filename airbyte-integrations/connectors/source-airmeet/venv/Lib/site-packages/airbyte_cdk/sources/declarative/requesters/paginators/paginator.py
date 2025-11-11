#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping, Optional

import requests

from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import (
    RequestOptionsProvider,
)
from airbyte_cdk.sources.types import Record, StreamSlice


@dataclass
class Paginator(ABC, RequestOptionsProvider):
    """
    Defines the token to use to fetch the next page of records from the API.

    If needed, the Paginator will set request options to be set on the HTTP request to fetch the next page of records.
    If the next_page_token is the path to the next page of records, then it should be accessed through the `path` method
    """

    @abstractmethod
    def get_initial_token(self) -> Optional[Any]:
        """
        Get the page token that should be included in the request to get the first page of records
        """

    @abstractmethod
    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any],
    ) -> Optional[Mapping[str, Any]]:
        """
        Returns the next_page_token to use to fetch the next page of records.

        :param response: the response to process
        :param last_page_size: the number of records read from the response
        :param last_record: the last record extracted from the response
        :param last_page_token_value: The current value of the page token made on the last request
        :return: A mapping {"next_page_token": <token>} for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
        pass

    @abstractmethod
    def path(
        self,
        next_page_token: Optional[Mapping[str, Any]],
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Optional[str]:
        """
        Returns the URL path to hit to fetch the next page of records

        e.g: if you wanted to hit https://myapi.com/v1/some_entity then this will return "some_entity"

        :return: path to hit to fetch the next request. Returning None means the path is not defined by the next_page_token
        """
        pass
