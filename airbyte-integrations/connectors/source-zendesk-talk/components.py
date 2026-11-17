# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
from dataclasses import dataclass
from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record


def is_cloud_edition() -> bool:
    # The platform sets AIRBYTE_EDITION on every connector job.
    return os.environ.get("AIRBYTE_EDITION", "").upper() == "CLOUD"


@dataclass
class IVRMenusRecordExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Record]:
        ivrs = response.json().get("ivrs", [])
        records = []
        for ivr in ivrs:
            for menu in ivr.get("menus", []):
                records.append({"ivr_id": ivr["id"], **menu})
        return records


@dataclass
class IVRRoutesRecordExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Record]:
        ivrs = response.json().get("ivrs", [])
        records = []
        for ivr in ivrs:
            for menu in ivr.get("menus", []):
                for route in menu.get("routes", []):
                    records.append({"ivr_id": ivr["id"], "ivr_menu_id": menu["id"], **route})
        return records


@dataclass
class ZendeskTalkAuthenticator(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    legacy_basic_auth: BasicHttpAuthenticator
    basic_auth: BasicHttpAuthenticator
    oauth: BearerAuthenticator
    oauth_refresh: DeclarativeSingleUseRefreshTokenOauth2Authenticator
    marketplace_headers: Mapping[str, str]

    def __new__(cls, legacy_basic_auth, basic_auth, oauth, oauth_refresh, config, marketplace_headers=None, *args, **kwargs):
        authenticator = cls._select(legacy_basic_auth, basic_auth, oauth, oauth_refresh, config)
        # In Airbyte Cloud every request comes from Airbyte's integration, whatever the credentials are. A self-managed
        # deployment is the user's own integration, so it does not send the headers.
        if marketplace_headers and is_cloud_edition():
            send_headers_on_every_request(authenticator, marketplace_headers)
        return authenticator

    @staticmethod
    def _select(legacy_basic_auth, basic_auth, oauth, oauth_refresh, config):
        credentials = config.get("credentials", {})
        if config.get("access_token", {}) and config.get("email", {}):
            return legacy_basic_auth
        elif credentials["auth_type"] == "api_token":
            return basic_auth
        elif credentials["auth_type"] == "oauth2.0":
            return oauth
        elif credentials["auth_type"] == "oauth2_refresh":
            return oauth_refresh
        else:
            raise Exception(f"Missing valid authenticator for auth_type: {credentials['auth_type']}")


def send_headers_on_every_request(authenticator: DeclarativeAuthenticator, headers: Mapping[str, str]) -> None:
    """
    Makes the authenticator add `headers` to every request it signs and to the OAuth token refresh request.

    The authenticator is the only component that every request to Zendesk passes through: the session calls it for each
    data request, and it sends the token refresh itself. The instance keeps its class, so the CDK treats it as before.
    """
    get_auth_header = authenticator.get_auth_header
    authenticator.get_auth_header = lambda: {**headers, **get_auth_header()}

    if hasattr(authenticator, "get_refresh_request_headers"):
        get_refresh_request_headers = authenticator.get_refresh_request_headers
        authenticator.get_refresh_request_headers = lambda: {**headers, **(get_refresh_request_headers() or {})}
