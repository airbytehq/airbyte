# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


CARDS_QUERY = {
    "list": "true",
    "sort": "-id",
    "members": "true",
    "pluginData": "true",
    "actions_display": "true",
    "customFieldItems": "true",
    "limit": "500",
}


def api_key_header(key: str, token: str) -> str:
    return f'OAuth oauth_consumer_key="{key}", oauth_token="{token}"'


class TrelloRequestBuilder:
    def __init__(self, config: dict):
        self.config = config
        self.authorization = api_key_header(config["key"], config["token"])

    def parent(self, name: str) -> HttpRequest:
        return self.get(f"members/me/{name}", {"since": self.config["start_date"]})

    def cards(self, board_id: str, before: str | None = None) -> HttpRequest:
        params = {**CARDS_QUERY, "since": self.config["start_date"]}
        if before:
            params["before"] = before
        return self.get(f"boards/{board_id}/cards/all", params)

    def get(self, path: str, params: dict) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.trello.com/1/{path}",
            query_params=params,
            headers={"Authorization": self.authorization},
        )
