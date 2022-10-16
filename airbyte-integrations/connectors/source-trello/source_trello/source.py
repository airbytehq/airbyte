#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

from .utils import TrelloRequestRateLimits as balancer


class TrelloStream(HttpStream, ABC):
    url_base = "https://api.trello.com/1/"

    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"

    # Page size
    limit = None

    extra_params = None

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=config["authenticator"])
        self.start_date = config["start_date"]
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit, "since": self.start_date}
        if next_page_token:
            params.update(**next_page_token)
        if self.extra_params:
            params.update(self.extra_params)
        return params

    @balancer.balance_rate_limit()
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        for record in json_response:
            yield record


class ChildStreamMixin:
    parent_stream_class: Optional[TrelloStream] = None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self.parent_stream_class(config=self.config).read_records(sync_mode=sync_mode):
            yield {"id": item["id"]}


class IncrementalTrelloStream(TrelloStream, ABC):
    cursor_field = "date"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()
        last_record = next(reversed(json_response), {})
        next_page = last_record.get("id")
        if next_page:
            return {"before": next_page}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if stream_state:
            params["since"] = stream_state[self.cursor_field]
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}


class Boards(TrelloStream):
    """Return list of all boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-boards-get
    Endpoint: https://api.trello.com/1/members/me/boards
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "members/me/boards"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        board_ids = self.config.get("board_ids", [])
        for record in super().parse_response(response, **kwargs):
            if not board_ids or record["id"] in board_ids:
                yield record


class Cards(ChildStreamMixin, TrelloStream):
    """Return list of all cards of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-get
    Endpoint: https://api.trello.com/1/boards/<id>/cards/all
    """

    parent_stream_class = Boards
    limit = 20000
    extra_params = {
        "customFieldItems": "true",
        "pluginData": "true",
        "actions_display": "true",
        "members": "true",
        "list": "true",
    }

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/cards/all"


class Checklists(ChildStreamMixin, TrelloStream):
    """Return list of all checklists of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-checklists-get
    Endpoint: https://api.trello.com/1/boards/<id>/checklists
    """

    parent_stream_class = Boards
    extra_params = {"fields": "all", "checkItem_fields": "all"}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/checklists"


class Lists(ChildStreamMixin, TrelloStream):
    """Return list of all lists of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-lists-get
    Endpoint: https://api.trello.com/1/boards/<id>/lists
    """

    parent_stream_class = Boards

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/lists"


class Users(ChildStreamMixin, TrelloStream):
    """Return list of all members of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-members-get
    Endpoint: https://api.trello.com/1/boards/<id>/members
    """

    parent_stream_class = Boards

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/members"


class Actions(ChildStreamMixin, IncrementalTrelloStream):
    """Return list of all actions of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-boardid-actions-get
    Endpoint: https://api.trello.com/1/boards/<id>/actions
    """

    parent_stream_class = Boards
    limit = 1000

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/actions"


class TrelloAuthenticator(HttpAuthenticator):
    """
    Generate auth header for start making requests from API token and API key.
    """

    def __init__(
        self,
        token: str,
        key: str,
        auth_header: str = "Authorization",
        key_header: str = "oauth_consumer_key",
        token_header: str = "oauth_token",
    ):
        self.auth_header = auth_header
        self.key_header = key_header
        self.token_header = token_header
        self._key = key
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f'OAuth {self.key_header}="{self._key}", {self.token_header}="{self._token}"'}


class SourceTrello(AbstractSource):
    """
    Source Trello fetch date from web-based, Kanban-style, list-making application.
    """

    @staticmethod
    def _get_authenticator(config: dict) -> TrelloAuthenticator:
        key, token = config["key"], config["token"]
        return TrelloAuthenticator(token=token, key=key)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the credentials.
        """

        try:
            url = f"{TrelloStream.url_base}members/me/boards"

            authenticator = self._get_authenticator(config)

            response = requests.get(url, headers=authenticator.get_auth_header())
            response.raise_for_status()
            available_boards = {row.get("id") for row in response.json()}
            for board_id in config.get("board_ids", []):
                if board_id not in available_boards:
                    return False, f"board_id {board_id} not found"

            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = self._get_authenticator(config)
        return [Actions(config), Boards(config), Cards(config), Checklists(config), Lists(config), Users(config)]
