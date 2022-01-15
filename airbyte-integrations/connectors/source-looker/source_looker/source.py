#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pendulum
import requests
from abc import ABC
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from datetime import datetime
from enum import Enum
from requests.auth import AuthBase
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

from .streams import LookerStream2, API_VERSION, SwaggerParser, LookerException


class CustomTokenAuthenticator(TokenAuthenticator):
    def __init__(self, domain: str, client_id: str, client_secret: str):
        self._domain, self._client_id, self._client_secret = domain, client_id, client_id
        super().__init__(None)

        self._access_token = None
        self._token_expiry_date = None

    def update_access_token(self) -> Optional[str]:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url = f"https://{self._domain}/api/{API_VERSION}/login"
        try:
            resp = requests.post(
                url=url, headers=headers, data=f"client_id={self._client_id}&client_secret={self._client_secret}"
            )
            if resp.status_code != 200:
                return "Unable to connect to the Looker API. Please check your credentials."
        except ConnectionError as error:
            return str(error)
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry_date = pendulum.now().add(seconds=data["expires_in"])
        return None

    def get_auth_header(self) -> Mapping[str, Any]:
        if not self._token_expiry_date or self._token_expiry_date < pendulum.now():
            err = self.update_access_token()
            if err:
                raise LookerException(f"auth error: {err}")
        return {"Authorization": f"token {self._access_token}"}


class SourceLooker(AbstractSource):
    """
    Source Intercom fetch data from messaging platform.
    """

    def get_authenticator(self, config: Mapping[str, Any]) -> CustomTokenAuthenticator:
        return CustomTokenAuthenticator(domain=config["domain"],
                                        client_id=config["client_id"],
                                        client_secret=config["client_secret"])

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        authenticator = self.get_authenticator(config)
        err = authenticator.update_access_token()
        if err:
            AirbyteLogger().error("auth error: {err}")
            return False, err
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)
        swagger_parser = SwaggerParser(domain=config["domain"])
        test_stream = LookerStream2(
            authenticator=authenticator,
            domain=config["domain"],
            run_look_ids=config.get("run_look_ids") or [],
            swagger_parser=swagger_parser)
        return [test_stream]
