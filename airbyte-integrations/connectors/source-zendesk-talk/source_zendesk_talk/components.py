# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, List, Mapping

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record


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

    def __new__(cls, legacy_basic_auth, basic_auth, oauth, config, *args, **kwargs):
        credentials = config.get("credentials", {})
        if config.get("access_token", {}) and config.get("email", {}):
            return legacy_basic_auth
        elif credentials["auth_type"] == "api_token":
            return basic_auth
        elif credentials["auth_type"] == "oauth2.0":
            return oauth
        else:
            raise Exception(f"Missing valid authenticator for auth_type: {credentials['auth_type']}")
