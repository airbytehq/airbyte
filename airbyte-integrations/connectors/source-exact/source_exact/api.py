# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any

import requests

from source_exact.auth import ExactOauth2Authenticator


class ExactAPI:
    def __init__(self, config):
        self.config = config
        self._authenticator: None | ExactOauth2Authenticator = None

    @property
    def authenticator(self) -> ExactOauth2Authenticator:
        if not self._authenticator:
            authenticator = ExactOauth2Authenticator(
                connector_config=self.config,
                token_refresh_endpoint=f"{self.config['base_url']}/api/oauth2/token",
                client_id=self.config["credentials"]["client_id"],
                client_secret=self.config["credentials"]["client_secret"],
            )
            self._authenticator = authenticator
        return self._authenticator

    def check_connection(self) -> tuple[bool, Any]:
        response = requests.get(
            url=f"{self.config['base_url']}/api/v1/current/Me?$select=CurrentDivision",
            headers=self.authenticator.get_auth_header(),
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            return False, exc.response.content
        return True, None
