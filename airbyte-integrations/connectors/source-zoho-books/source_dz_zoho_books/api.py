#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from types import MappingProxyType
from typing import Any, Mapping, Tuple

import requests

from .auth import ZohoBooksAuthenticator

logger = logging.getLogger(__name__)


class ZohoBooksAPI:
    _DC_REGION_TO_ACCESS_URL = MappingProxyType(
        {
            "US": "https://accounts.zoho.com",
            "AU": "https://accounts.zoho.com.au",
            "EU": "https://accounts.zoho.eu",
            "IN": "https://accounts.zoho.in",
            "JP": "https://accounts.zoho.jp",
        }
    )
    _DC_REGION_TO_API_URL = MappingProxyType(
        {
            "US": "https://www.zohoapis.com/books/",
            "AU": "https://www.zohoapis.com.au/books/",
            "EU": "https://www.zohoapis.eu/books/",
            "IN": "https://www.zohoapis.in/books/",
            "JP": "https://www.zohoapis.jp/books/",
        }
    )

    def __init__(self, config: Mapping[str, Any]):
        self.config = config
        self._authenticator = None

    @property
    def authenticator(self) -> ZohoBooksAuthenticator:
        if self._authenticator is None:
            authenticator = ZohoBooksAuthenticator(
                token_refresh_endpoint=f"{self._access_url}/oauth/v2/token",
                client_id=self.config["client_id"],
                client_secret=self.config["client_secret"],
                refresh_token=self.config["refresh_token"],
            )
            self._authenticator = authenticator
        return self._authenticator

    @property
    def _access_url(self) -> str:
        return self._DC_REGION_TO_ACCESS_URL[self.config["dc_region"].upper()]

    @property
    def api_url(self) -> str:
        url = self._DC_REGION_TO_API_URL[self.config["dc_region"].upper()]
        return url

    def check_connection(self) -> Tuple[bool, Any]:
        path = "v3/items"
        response = requests.get(url=f"{self.api_url}{path}", headers=self.authenticator.get_auth_header())
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            return False, exc.response.content
        return True, None
