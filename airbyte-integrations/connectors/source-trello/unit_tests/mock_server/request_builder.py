# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class TrelloRequestBuilder:
    def __init__(self, config: dict):
        self.config = config

    def parent(self, name: str) -> HttpRequest:
        return self._build(f"members/me/{name}", {"since": self.config["start_date"]})

    def cards(self, board_id: str, before: str | None = None) -> HttpRequest:
        params = {
            "list": "true",
            "sort": "-id",
            "since": self.config["start_date"],
            "members": "true",
            "pluginData": "true",
            "actions_display": "true",
            "customFieldItems": "true",
            "limit": "500",
        }
        if before:
            params["before"] = before
        return self._build(f"boards/{board_id}/cards/all", params)

    def _build(self, path: str, params: dict) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.trello.com/1/{path}",
            query_params=params,
            headers={"Authorization": f'OAuth oauth_consumer_key="{self.config["key"]}", oauth_token="{self.config["token"]}"'},
        )
