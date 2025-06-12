#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, MutableMapping, Tuple

import requests
from requests.auth import HTTPBasicAuth

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from source_tplcentral.streams import Customers, Inventory, Items, Orders, StockDetails, StockSummaries


class TplcentralAuthenticator(Oauth2Authenticator):
    def __init__(
        self,
        token_refresh_endpoint: str,
        client_id: str,
        client_secret: str,
        user_login_id: int = None,
        user_login: str = None,
        scopes: List[str] = None,
    ):
        super().__init__(
            token_refresh_endpoint=token_refresh_endpoint,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=None,
        )

        self.token_refresh_endpoint = token_refresh_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.access_token_name = "access_token"
        self.expires_in_name = "expires_in"
        self.user_login_id = user_login_id
        self.user_login = user_login

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
        }

        if self.scopes:
            payload["scopes"] = self.scopes

        if self.user_login_id:
            payload["user_login_id"] = self.user_login_id

        if self.user_login:
            payload["user_login"] = self.user_login

        return payload

    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.post(
                self.token_refresh_endpoint, auth=HTTPBasicAuth(self.client_id, self.client_secret), json=self.get_refresh_request_body()
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json[self.access_token_name], response_json[self.expires_in_name]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class SourceTplcentral(AbstractSource):
    def _auth(self, config):
        return TplcentralAuthenticator(
            token_refresh_endpoint=f"{config['url_base']}AuthServer/api/Token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            user_login_id=config.get("user_login_id"),
            user_login=config.get("user_login"),
        )

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            self._auth(config).get_auth_header()
        except Exception as e:
            return None, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = self._auth(config)

        return [
            StockSummaries(config),
            Customers(config),
            Items(config),
            StockDetails(config),
            Inventory(config),
            Orders(config),
        ]
