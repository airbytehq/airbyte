#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from enum import Enum
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


class AirbyteType(Enum):
    String = {"type": ["null", "string"]}
    Boolean = {"type": ["null", "boolean"]}
    Timestamp = {"type": ["null", "string"], "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
    Integer = {"type": ["null", "integer"]}
    Number = {"type": ["null", "number"]}


class DataverseType(Enum):
    String = AirbyteType.String
    Uniqueidentifier = AirbyteType.String
    DateTime = AirbyteType.Timestamp
    Integer = AirbyteType.Integer
    BigInt = AirbyteType.Integer
    Money = AirbyteType.Number
    Boolean = AirbyteType.Boolean
    Double = AirbyteType.Number
    Decimal = AirbyteType.Number
    Status = AirbyteType.Integer
    State = AirbyteType.Integer
    Picklist = AirbyteType.Integer
    Lookup = AirbyteType.String
    Virtual = None


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
    if dataverse_type in DataverseType.__members__:
        enum_type = DataverseType[dataverse_type]
        if enum_type:
            return enum_type.value if enum_type.value is None else enum_type.value.value

    return AirbyteType.String.value
