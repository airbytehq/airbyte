#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import base64
from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from mailchimp3 import MailChimp
from requests.auth import AuthBase

from .streams import Campaigns, EmailActivity, Lists


class MailChimpAuthenticator:
    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> AuthBase:
        authorization = config.get("authorization", {})
        auth_type = authorization.get("auth_type")
        if auth_type == "Apikey" or not authorization:
            # API keys have the format <key>-<data_center>.
            # See https://mailchimp.com/developer/marketing/docs/fundamentals/#api-structure
            apikey = authorization.get("apikey") or config.get("apikey")
            if not apikey:
                raise Exception("No apikey in creds")
            auth_string = f"anystring:{apikey}".encode("utf8")
            b64_encoded = base64.b64encode(auth_string).decode("utf8")
            auth = TokenAuthenticator(token=b64_encoded, auth_method="Basic")
            auth.data_center = apikey.split("-").pop()

        elif auth_type == "Oauth":
            auth = TokenAuthenticator(token=authorization["access_token"], auth_method="Bearer")
            auth.data_center = authorization["server_prefix"]

        else:
            raise Exception(f"Invalid auth type: {auth_type}")

        auth.auth_type = auth_type
        return auth


class SourceMailchimp(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authorization = config.get("authorization", {})
            apikey = authorization.get("apikey") or config.get("apikey")
            username = authorization.get("username") or config.get("username")
            access_token = authorization.get("access_token")
            client = MailChimp(mc_api=apikey, mc_user=username, access_token=access_token)
            client.ping.get()
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = MailChimpAuthenticator.get_auth(config)
        streams_ = [Lists(authenticator=authenticator), Campaigns(authenticator=authenticator), EmailActivity(authenticator=authenticator)]

        return streams_
