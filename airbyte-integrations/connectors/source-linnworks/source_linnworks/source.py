#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, MutableMapping, Tuple

import pendulum
import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .streams import ProcessedOrderDetails, ProcessedOrders, StockItems, StockLocationDetails, StockLocations


class LinnworksAuthenticator(Oauth2Authenticator):
    def __init__(
        self,
        application_id: str,
        application_secret: str,
        token: str,
        token_expiry_date: pendulum.datetime = None,
        token_refresh_endpoint: str = "https://api.linnworks.net/api/Auth/AuthorizeByApplication",
        access_token_name: str = "Token",
        expires_in_name: str = "TTL",
        server_name: str = "Server",
    ):
        super().__init__(
            token_refresh_endpoint,
            application_id,
            application_secret,
            token,
            scopes=None,
            token_expiry_date=token_expiry_date,
            access_token_name=access_token_name,
            expires_in_name=expires_in_name,
        )
        self.access_token_name = access_token_name
        self.application_id = application_id
        self.application_secret = application_secret
        self.expires_in_name = expires_in_name
        self.token = token
        self.server_name = server_name
        self.token_refresh_endpoint = token_refresh_endpoint

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": self.get_access_token()}

    def get_access_token(self):
        if self.token_has_expired():
            t0 = pendulum.now()
            token, expires_in, server = self.refresh_access_token()
            self._access_token = token
            self._token_expiry_date = t0.add(seconds=expires_in)
            self._server = server

        return self._access_token

    def get_server(self):
        if self.token_has_expired():
            self.get_access_token()

        return self._server

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "applicationId": self.application_id,
            "applicationSecret": self.application_secret,
            "token": self.token,
        }

        return payload

    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint, data=self.get_refresh_request_body())
            response.raise_for_status()
            response_json = response.json()
            return response_json[self.access_token_name], response_json[self.expires_in_name], response_json[self.server_name]
        except Exception as e:
            try:
                e = Exception(response.json()["Message"])
            except Exception:
                # Unable to get an error message from the response body.
                # Continue with the original error.
                pass
            raise Exception(f"Error while refreshing access token: {e}") from e


class SourceLinnworks(AbstractSource):
    def _auth(self, config):
        return LinnworksAuthenticator(
            token_refresh_endpoint="https://api.linnworks.net/api/Auth/AuthorizeByApplication",
            application_id=config["application_id"],
            application_secret=config["application_secret"],
            token=config["token"],
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            self._auth(config).get_auth_header()
        except Exception as error:
            return False, f"Unable to connect to Linnworks API with the provided credentials: {error}"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._auth(config)
        return [
            StockLocations(authenticator=auth),
            StockLocationDetails(authenticator=auth),
            StockItems(authenticator=auth),
            ProcessedOrders(authenticator=auth, start_date=config["start_date"]),
            ProcessedOrderDetails(authenticator=auth, start_date=config["start_date"]),
        ]
