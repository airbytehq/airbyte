#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import datetime
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .auth import TrelloAuthenticator
from .utils import TrelloRequestRateLimits as balancer
from .utils import read_all_boards


class TrelloStream(HttpStream, ABC):
    url_base = "https://api.trello.com/1/"

    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"

    # Page size
    limit = None

    extra_params = None

    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

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
    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        board_ids = set(self.config.get("board_ids", []))
        for board_id in read_all_boards(Boards(self.config), Organizations(self.config)):
            if not board_ids or board_id in board_ids:
                yield {"id": board_id}


class IncrementalTrelloStream(TrelloStream, ABC):
    cursor_field = "date"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        if response_json:
            return {"before": response_json[-1]["id"]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if stream_state:
            board_id = stream_slice["id"]
            since = stream_state.get(board_id, {}).get(self.cursor_field)
            if since:
                params["since"] = since
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        board_id = latest_record["data"]["board"]["id"]
        updated_state = latest_record[self.cursor_field]
        stream_state_value = current_stream_state.get(board_id, {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state.setdefault(board_id, {})[self.cursor_field] = updated_state
        return current_stream_state


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

    limit = 500
    extra_params = {
        "customFieldItems": "true",
        "pluginData": "true",
        "actions_display": "true",
        "members": "true",
        "list": "true",
        "sort": "-id",
    }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        if response_json:
            return {"before": response_json[-1]["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/cards/all"


class Checklists(ChildStreamMixin, TrelloStream):
    """Return list of all checklists of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-checklists-get
    Endpoint: https://api.trello.com/1/boards/<id>/checklists
    """

    extra_params = {"fields": "all", "checkItem_fields": "all"}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/checklists"


class Lists(ChildStreamMixin, TrelloStream):
    """Return list of all lists of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-lists-get
    Endpoint: https://api.trello.com/1/boards/<id>/lists
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/lists"


class Organizations(TrelloStream):
    """Return list of all member's organizations
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-members/#api-members-id-organizations-get
    Endpoint: https://api.trello.com/1/members/me/organizations
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "members/me/organizations"


class Users(ChildStreamMixin, TrelloStream):
    """Return list of all members of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-members-get
    Endpoint: https://api.trello.com/1/boards/<id>/members
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/members"


class Actions(ChildStreamMixin, IncrementalTrelloStream):
    """Return list of all actions of a boards.
    API Docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-boardid-actions-get
    Endpoint: https://api.trello.com/1/boards/<id>/actions
    """

    limit = 1000

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['id']}/actions"


class SourceTrello(AbstractSource):
    """
    Source Trello fetch date from web-based, Kanban-style, list-making application.
    """

    def _validate_and_transform(self, config: Mapping[str, Any]):
        datetime.datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%SZ")
        return config

    @staticmethod
    def _get_authenticator(config: dict):
        return TrelloAuthenticator(apiKey=config["key"], apiToken=config["token"])

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the credentials.
        """

        config = self._validate_and_transform(config)
        config["authenticator"] = self._get_authenticator(config)
        available_boards = set(read_all_boards(Boards({**config, "board_ids": []}), Organizations(config)))
        unknown_boards = set(config.get("board_ids", [])) - available_boards
        if unknown_boards:
            unknown_boards = ", ".join(sorted(unknown_boards))
            return False, f"Board ID(s): {unknown_boards} not found"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = self._get_authenticator(config)
        return [Actions(config), Boards(config), Cards(config), Checklists(config), Lists(config), Users(config), Organizations(config)]
