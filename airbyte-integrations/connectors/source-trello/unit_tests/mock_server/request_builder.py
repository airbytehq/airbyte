# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import urlencode

from airbyte_cdk.test.mock_http import HttpRequest


TOKEN_URL = "https://auth.atlassian.com/oauth/token"

CARDS_QUERY = {
    "list": "true",
    "sort": "-id",
    "members": "true",
    "pluginData": "true",
    "actions_display": "true",
    "customFieldItems": "true",
    "limit": "500",
}

# Path and query parameters of each stream's first request, besides `since`.
STREAM_ENDPOINTS = {
    "boards": ("members/me/boards", {}),
    "organizations": ("members/me/organizations", {}),
    "actions": ("boards/{board_id}/actions", {"limit": "500"}),
    "cards": ("boards/{board_id}/cards/all", CARDS_QUERY),
    "checklists": ("boards/{board_id}/checklists", {"fields": "all", "checkItem_fields": "all"}),
    "lists": ("boards/{board_id}/lists", {}),
    "users": ("boards/{board_id}/members", {}),
}
PAGINATED_STREAMS = {"actions", "cards"}


def api_key_header(config: dict) -> str:
    credentials = config.get("credentials") or config
    return f'OAuth oauth_consumer_key="{credentials["key"]}", oauth_token="{credentials["token"]}"'


def refresh_request(client_id: str, client_secret: str, refresh_token: str) -> HttpRequest:
    body = {"grant_type": "refresh_token", "client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token}
    return HttpRequest(url=TOKEN_URL, body=urlencode(body))


class TrelloRequestBuilder:
    def __init__(self, config: dict, authorization: str | None = None):
        self.config = config
        self.authorization = authorization or api_key_header(config)

    def parent(self, name: str) -> HttpRequest:
        return self.stream(name)

    def cards(self, board_id: str, before: str | None = None) -> HttpRequest:
        return self.stream("cards", board_id, before)

    def stream(self, name: str, board_id: str = "", before: str | None = None) -> HttpRequest:
        path, params = STREAM_ENDPOINTS[name]
        since = self.config["start_date"]
        if name == "actions":
            # The actions cursor sends its slice start in its own datetime format, with microseconds.
            since = since.replace("Z", ".000000Z")
        params = {**params, "since": since}
        if before:
            params["before"] = before
        return self.get(path.format(board_id=board_id), params)

    def get(self, path: str, params: dict) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.trello.com/1/{path}",
            query_params=params,
            headers={"Authorization": self.authorization},
        )
