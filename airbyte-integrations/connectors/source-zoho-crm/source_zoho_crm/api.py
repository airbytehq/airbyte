#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from types import MappingProxyType
from typing import Any, Mapping, Tuple

import requests

from .auth import ZohoOauth2Authenticator


class ZohoAPI:
    _DC_REGION_TO_ACCESS_URL = MappingProxyType(
        {
            "US": "https://accounts.zoho.com",
            "AU": "https://accounts.zoho.com.au",
            "EU": "https://accounts.zoho.eu",
            "IN": "https://accounts.zoho.in",
            "CN": "https://accounts.zoho.com.cn",
            "JP": "https://accounts.zoho.jp",
        }
    )
    _DC_REGION_TO_API_URL = MappingProxyType(
        {
            "US": "https://zohoapis.com",
            "AU": "https://zohoapis.com.au",
            "EU": "https://zohoapis.eu",
            "IN": "https://zohoapis.in",
            "CN": "https://zohoapis.com.cn",
            "JP": "https://zohoapis.jp",
        }
    )
    _API_ENV_TO_URL_PREFIX = MappingProxyType({"production": "", "developer": "developer", "sandbox": "sandbox"})
    _CONCURRENCY_API_LIMITS = MappingProxyType({"Free": 5, "Standard": 10, "Professional": 15, "Enterprise": 20, "Ultimate": 25})

    def __init__(self, config: Mapping[str, Any]):
        self.config = config
        self._authenticator = None

    @property
    def authenticator(self) -> ZohoOauth2Authenticator:
        if not self._authenticator:
            credentials = self.config["credentials"]
            authenticator = ZohoOauth2Authenticator(
                f"{self._access_url}/oauth/v2/token", credentials["client_id"], credentials["client_secret"], credentials["refresh_token"]
            )
            self._authenticator = authenticator
        return self._authenticator

    @property
    def _access_url(self) -> str:
        return self._DC_REGION_TO_ACCESS_URL[self.config["dc_region"].upper()]

    @property
    def max_concurrent_requests(self) -> int:
        return self._CONCURRENCY_API_LIMITS[self.config["edition"]]

    @property
    def api_url(self) -> str:
        schema, domain = self._DC_REGION_TO_API_URL[self.config["dc_region"].upper()].split("://")
        prefix = self._API_ENV_TO_URL_PREFIX[self.config["environment"].lower()]
        if prefix:
            domain = f"{prefix}.{domain}"
        return f"{schema}://{domain}"

    def module_settings(self, module_name: str) -> "requests.models.Response":
        path = f"/crm/v2/settings/modules/{module_name}"
        return requests.get(url=f"{self.api_url}{path}", headers=self.authenticator.get_auth_header())

    def modules_settings(self) -> "requests.models.Response":
        path = "/crm/v2/settings/modules"
        return requests.get(url=f"{self.api_url}{path}", headers=self.authenticator.get_auth_header())

    def fields_settings(self, module_name: str) -> "requests.models.Response":
        path = "/crm/v2/settings/fields"
        return requests.get(url=f"{self.api_url}{path}", params={"module": module_name}, headers=self.authenticator.get_auth_header())

    def check_connection(self) -> Tuple[bool, Any]:
        http_response = self.modules_settings()
        try:
            http_response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            return False, exc.response.content
        return True, None
