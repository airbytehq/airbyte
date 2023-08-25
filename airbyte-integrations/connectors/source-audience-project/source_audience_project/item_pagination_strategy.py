import logging
import requests
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Optional, Union, List, Tuple, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement


# @dataclass
# class AuthenticatorSquare(DeclarativeAuthenticator):
#     config: Mapping[str, Any]
#     bearer: BearerAuthenticator
#     oauth: DeclarativeOauth2Authenticator
#
#     def __new__(cls, bearer, oauth, config, *args, **kwargs):
#         if config.get("credentials", {}).get("access_token"):
#             return bearer
#         else:
#             return oauth


class ItemPaginationStrategy(PageIncrement):

    def __post_init__(self, parameters: Mapping[str, Any]):
        # `self._page` corresponds to board page number
        # `self._sub_page` corresponds to item page number within its board
        self.start: int = self.start_from_page
        self._page: Optional[int] = self.start
        self._max_results: Optional[int] = self.page_size
        print("self.start", self.start)
        print("self._page", self._page)
        print("self._max_results", self._max_results)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        self._page += self._max_results
        record_len = len(response.json().get("data"))
        print("_page", self._page)
        print("record_len", record_len)
        print("_max_results", self._max_results)
        if record_len < self._max_results or record_len == 0:
            print("Here1")
            return None
        print("Here2")
        return self._page, self._max_results

    def get_request_params(
            self,
            *,
            stream_state: Optional[StreamState] = None,
            stream_slice: Optional[StreamSlice] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        page = next_page_token and next_page_token["next_page_token"]
        print("HERE111111:", page)
        start_result, max_result = page if page else (None, None)
        return {"start": start_result, "maxResults": max_result}


class ItemPathStrategy(HttpRequester):

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "campaigns"






