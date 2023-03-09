#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import base64
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from requests.auth import AuthBase

from .streams import Campaigns, EmailActivity, Lists


class MailChimpAuthenticator:
    @staticmethod
    def get_server_prefix(access_token: str) -> str:
        try:
            response = requests.get(
                "https://login.mailchimp.com/oauth2/metadata", headers={"Authorization": "OAuth {}".format(access_token)}
            )
            return response.json()["dc"]
        except Exception as e:
            raise Exception(f"Cannot retrieve server_prefix for you account. \n {repr(e)}")

    def get_auth(self, config: Mapping[str, Any]) -> AuthBase:
        authorization = config.get("credentials", {})
        auth_type = authorization.get("auth_type")
        if auth_type == "apikey" or not authorization:
            # API keys have the format <key>-<data_center>.
            # See https://mailchimp.com/developer/marketing/docs/fundamentals/#api-structure
            apikey = authorization.get("apikey") or config.get("apikey")
            if not apikey:
                raise Exception("No apikey in creds")
            auth_string = f"anystring:{apikey}".encode("utf8")
            b64_encoded = base64.b64encode(auth_string).decode("utf8")
            auth = TokenAuthenticator(token=b64_encoded, auth_method="Basic")
            auth.data_center = apikey.split("-").pop()

        elif auth_type == "oauth2.0":
            access_token = authorization["access_token"]
            auth = TokenAuthenticator(token=access_token, auth_method="Bearer")
            auth.data_center = self.get_server_prefix(access_token)

        else:
            raise Exception(f"Invalid auth type: {auth_type}")

        return auth


class SourceMailchimp(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = MailChimpAuthenticator().get_auth(config)
            requests.get(f"https://{authenticator.data_center}.api.mailchimp.com/3.0/ping", headers=authenticator.get_auth_header())
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = MailChimpAuthenticator().get_auth(config)
        campaign_id = config.get("campaign_id")
        return [
            Lists(authenticator=authenticator),
            Campaigns(authenticator=authenticator),
            EmailActivity(authenticator=authenticator, campaign_id=campaign_id),
        ]
