#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urljoin
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


# Basic full refresh stream
class TodoistStream(HttpStream, ABC):
    """
    Stream for Todoist REST API : https://developer.todoist.com/rest/v2/#overview
    """

    REST_VERSION = "v2"
    url_base = urljoin("https://api.todoist.com", f"/rest/{REST_VERSION}/")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class Tasks(TodoistStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        https://api.todoist.com/rest/v2/tasks
        """
        return "tasks"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()

class Projects(TodoistStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        https://api.todoist.com/rest/v2/projects
        """
        return "projects"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


# Source
class SourceTodoist(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            token = config["token"]
            authenticator = TokenAuthenticator(token=token)
            task_stream = Tasks(authenticator)
            task_records = task_stream.read_records(sync_mode="full_refresh")
            record = next(task_records)
        except Exception as e:
            return False, e
        else:
            logger.info(f"Successfully connected to Tasks stream. Pulled one record: {record}")
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        token = config["token"]
        auth = TokenAuthenticator(token=token)  # Oauth2Authenticator is also available if you need oauth support
        return [Tasks(authenticator=auth), Projects(authenticator=auth)]
