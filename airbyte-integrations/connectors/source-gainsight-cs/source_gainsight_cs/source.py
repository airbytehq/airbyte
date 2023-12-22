#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

from .streams import (
    GainsightCsStream,
    Person
)


class GainsightCsAuthenticator(HttpAuthenticator):
    def __init__(self, token: str):
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"AccessKey": self._token}


class SourceGainsightCs(AbstractSource):
    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]) -> HttpAuthenticator:
        token = config.get("access_key")
        return GainsightCsAuthenticator(token)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = f"{GainsightCsStream.url_base}meta/services/objects/Person/describe?idd=true"
        auth = SourceGainsightCs._get_authenticator(config)
        try:
            session = requests.get(url, headers=auth.get_auth_header())
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._get_authenticator(config)
        return [
            Person(authenticator=auth)
        ]
