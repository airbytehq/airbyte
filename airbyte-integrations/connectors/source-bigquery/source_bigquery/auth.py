#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Union

import json
import requests
import httplib2
from google.auth.crypt import RSASigner
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.service_account import ServiceAccountCredentials, _JWTAccessCredentials
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.requests_native_auth import (
    BasicHttpAuthenticator,
    Oauth2Authenticator,
    TokenAuthenticator,
)
from airbyte_cdk.utils import AirbyteTracedException

# class BigqueryServiceAccountCredentials(ServiceAccountCredentials):


class BigqueryOAuth(Oauth2Authenticator):
    """
    """
    pass


class BigqueryAuth:
    def __new__(cls, config: dict) -> Union[ServiceAccountCredentials, BigqueryOAuth, Oauth2Authenticator, TokenAuthenticator]:       
        # for new oauth configs
        credentials_json = config["credentials_json"]
        credentials_json = json.loads(config["credentials_json"], strict=False)

        credentials = ServiceAccountCredentials(credentials_json["client_email"], RSASigner.from_string(credentials_json["private_key"], credentials_json["private_key_id"]),\
                                                scopes=['https://www.googleapis.com/auth/bigquery', 'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/devstorage.full_control'], \
                                                private_key_id=credentials_json["private_key_id"], client_id=credentials_json["client_id"])
        h = httplib2.Http()
        h = credentials.authorize(h)
        sc = credentials.create_scoped(scopes=['https://www.googleapis.com/auth/bigquery', 'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/cloud-platform.read-only'])
        token = sc.get_access_token()
        access_token = str(token.access_token)
        auth = TokenAuthenticator(token=access_token)
        
        return auth
    