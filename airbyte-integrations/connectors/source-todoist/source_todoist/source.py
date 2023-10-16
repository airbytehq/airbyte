#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


# Basic full refresh stream
class TodoistStream(HttpStream):
    """
    Stream for Todoist REST API : https://developer.todoist.com/rest/v2/#overview
    """

    @property
    def url_base(self) -> str:
        return "https://api.todoist.com/rest/v2/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.name.title().lower()


class Tasks(TodoistStream):

    primary_key = "id"


class Projects(TodoistStream):

    primary_key = "id"


# Source
class SourceTodoist(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            token = config["token"]
            authenticator = TokenAuthenticator(token=token)
            task_stream = Tasks(authenticator)
            task_records = task_stream.read_records(sync_mode="full_refresh")
            next(task_records)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        token = config["token"]
        auth = TokenAuthenticator(token=token)  # Oauth2Authenticator is also available if you need oauth support
        return [Tasks(authenticator=auth), Projects(authenticator=auth)]
