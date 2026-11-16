# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, List, Mapping, MutableMapping

import requests

from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.transformations.config_transformations.config_transformation import ConfigTransformation
from airbyte_cdk.sources.declarative.types import Record


# `credentials.auth_type` values that the Airbyte Cloud spec hides from the setup form. Zendesk removes API tokens on
# April 30, 2027, and the legacy OAuth option has no refresh token. Sources that already use them keep working.
AUTH_TYPES_HIDDEN_IN_CLOUD = frozenset({"api_token", "oauth2.0"})

# The manifest description recommends an API token to self-managed users, which the Airbyte Cloud form no longer offers.
CREDENTIALS_DESCRIPTION_IN_CLOUD = (
    "Authenticate with `OAuth2.0`. Sources that already use an API token or the legacy OAuth option keep working. "
    "Zendesk deactivates all API tokens on April 30, 2027, so re-authenticate those sources with OAuth before then."
)


def is_cloud_edition() -> bool:
    # The platform sets AIRBYTE_EDITION on every connector job. The spec published for Cloud is generated with it too.
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

    def __new__(cls, legacy_basic_auth, basic_auth, oauth, oauth_refresh, config, *args, **kwargs):
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


class HideDeprecatedAuthOptionsInCloud(ConfigTransformation):
    """
    Marks a spec whose Airbyte Cloud variant offers only the refresh-token OAuth option.

    `manifest.yaml` lists this class under `spec.config_normalization_rules.transformations`. That reference is what
    makes the CDK load this module for the `spec` command, and `generate_spec_for_edition` changes only a spec that
    carries the marker. The config itself is never changed, so a source that uses a hidden option still passes
    check, discover and read.
    """

    def transform(self, config: MutableMapping[str, Any]) -> None:
        pass


def cloud_connection_specification(connection_specification: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Returns a copy in which the setup form offers only the refresh-token OAuth option.

    `airbyte_hidden` is a hint for the form. The hidden options stay in the schema, so a saved config that uses one of
    them is still valid.
    """
    specification = deepcopy(dict(connection_specification))
    credentials = specification["properties"]["credentials"]
    for option in credentials["oneOf"]:
        if option["properties"]["auth_type"]["const"] in AUTH_TYPES_HIDDEN_IN_CLOUD:
            option["airbyte_hidden"] = True
    credentials["description"] = CREDENTIALS_DESCRIPTION_IN_CLOUD
    return specification


_generate_spec = Spec.generate_spec


def generate_spec_for_edition(self: Spec) -> ConnectorSpecification:
    specification = _generate_spec(self)
    is_marked = any(isinstance(transformation, HideDeprecatedAuthOptionsInCloud) for transformation in self.config_transformations)
    if is_marked and is_cloud_edition():
        specification.connectionSpecification = cloud_connection_specification(specification.connectionSpecification)
    return specification


# A manifest cannot vary its spec by edition, and the `Spec` component has no extension point, so the method is replaced.
Spec.generate_spec = generate_spec_for_edition
