#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping, Union

import httplib2
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from google.auth.crypt import RSASigner
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/cloud-platform.read-only",
]


class BigqueryAuth:
    def __new__(cls, config: dict) -> Union[ServiceAccountCredentials, Oauth2Authenticator, TokenAuthenticator]:
        credentials_json = json.loads(config["credentials_json"], strict=False)

        credentials = ServiceAccountCredentials(
            credentials_json["client_email"],
            RSASigner.from_string(credentials_json["private_key"], credentials_json["private_key_id"]),
            scopes=SCOPES,
            private_key_id=credentials_json["private_key_id"],
            client_id=credentials_json["client_id"],
        )
        h = httplib2.Http()
        credentials.authorize(h)
        token = credentials.get_access_token()

        return TokenAuthenticator(token=str(token.access_token))
