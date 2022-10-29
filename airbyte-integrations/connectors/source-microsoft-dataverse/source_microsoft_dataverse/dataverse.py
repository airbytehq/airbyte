#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator


class MicrosoftOauth2Authenticator(Oauth2Authenticator):
    def build_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Returns the request body to set on the refresh request
        """
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
            "scope": self.get_scopes(),
        }

        return payload


def get_auth(config: Mapping[str, Any]) -> MicrosoftOauth2Authenticator:
    return MicrosoftOauth2Authenticator(
        token_refresh_endpoint=f'https://login.microsoftonline.com/{config["tenant_id"]}/oauth2/v2.0/token',
        client_id=config["client_id"],
        client_secret=config["client_secret_value"],
        scopes=[f'{config["url"]}/.default'],
        refresh_token="",
    )


def do_request(config: Mapping[str, Any], path: str):
    auth = get_auth(config)
    headers = auth.get_auth_header()
    # Call a protected API with the access token.
    return requests.get(
        config["url"] + "/api/data/v9.2/" + path,
        headers=headers,
    )


def convert_dataverse_type(dataverse_type: str) -> Optional[dict]:
    if dataverse_type == "String":
        attribute_type = {"type": ["null", "string"]}
    elif dataverse_type == "DateTime":
        attribute_type = {"type": ["null", "string"], "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
    elif dataverse_type == "Integer":
        attribute_type = {"type": ["null", "integer"]}
    elif dataverse_type == "Money":
        attribute_type = {"type": ["null", "number"]}
    elif dataverse_type == "Boolean":
        attribute_type = {"type": ["null", "boolean"]}
    elif dataverse_type == "Double":
        attribute_type = {"type": ["null", "number"]}
    elif dataverse_type == "Decimal":
        attribute_type = {"type": ["null", "number"]}
    elif dataverse_type == "Virtual":
        return None
    else:
        attribute_type = {"type": ["null", "string"]}

    return attribute_type
