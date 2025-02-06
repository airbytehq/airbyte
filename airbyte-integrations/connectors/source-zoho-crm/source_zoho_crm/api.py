#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from types import MappingProxyType
from typing import Any, List, Mapping, MutableMapping, Tuple
from urllib.parse import urlsplit, urlunsplit

import requests

from .auth import ZohoOauth2Authenticator


logger = logging.getLogger(__name__)


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
            authenticator = ZohoOauth2Authenticator(
                f"{self._access_url}/oauth/v2/token", self.config["client_id"], self.config["client_secret"], self.config["refresh_token"]
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
        schema, domain, *_ = urlsplit(self._DC_REGION_TO_API_URL[self.config["dc_region"].upper()])
        prefix = self._API_ENV_TO_URL_PREFIX[self.config["environment"].lower()]
        if prefix:
            domain = f"{prefix}.{domain}"
        return urlunsplit((schema, domain, *_))

    def _json_from_path(self, path: str, key: str, params: MutableMapping[str, str] = None) -> List[MutableMapping[Any, Any]]:
        response = requests.get(url=f"{self.api_url}{path}", headers=self.authenticator.get_auth_header(), params=params or {})
        if response.status_code == 204:
            # Zoho CRM returns `No content` for Metadata of some modules
            logger.warning(f"{key.capitalize()} Metadata inaccessible: {response.content} [HTTP status {response.status_code}]")
            return []
        return response.json()[key]

    def module_settings(self, module_name: str) -> List[MutableMapping[Any, Any]]:
        return self._json_from_path(f"/crm/v2/settings/modules/{module_name}", key="modules")

    def modules_settings(self) -> List[MutableMapping[Any, Any]]:
        return self._json_from_path("/crm/v2/settings/modules", key="modules")

    def fields_settings(self, module_name: str) -> List[MutableMapping[Any, Any]]:
        return self._json_from_path("/crm/v2/settings/fields", key="fields", params={"module": module_name})

    def check_connection(self) -> Tuple[bool, Any]:
        path = "/crm/v2/settings/modules"
        response = requests.get(url=f"{self.api_url}{path}", headers=self.authenticator.get_auth_header())
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            return False, exc.response.content
        return True, None
