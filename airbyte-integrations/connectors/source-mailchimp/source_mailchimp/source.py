#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import base64
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from requests.auth import AuthBase

from .streams import Automations, Campaigns, EmailActivity, ListMembers, Lists, Reports, Segments, Unsubscribes


class MailChimpAuthenticator:
    @staticmethod
    def get_oauth_data_center(access_token: str) -> str:
        """
        Every Mailchimp API request must be sent to a specific data center.
        The data center is already embedded in API keys, but not OAuth access tokens.
        This method retrieves the data center for OAuth credentials.
        """
        try:
            response = requests.get(
                "https://login.mailchimp.com/oauth2/metadata", headers={"Authorization": "OAuth {}".format(access_token)}
            )

            # Requests to this endpoint will return a 200 status code even if the access token is invalid.
            error = response.json().get("error")
            if error == "invalid_token":
                raise ValueError("The access token you provided was invalid. Please check your credentials and try again.")
            return response.json()["dc"]
        except Exception as e:
            raise Exception(f"An exception occured while retrieving the data center for your account. \n {repr(e)}")

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
            auth.data_center = self.get_oauth_data_center(access_token)

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
            Automations(authenticator=authenticator),
            Campaigns(authenticator=authenticator),
            EmailActivity(authenticator=authenticator, campaign_id=campaign_id),
            Lists(authenticator=authenticator),
            ListMembers(authenticator=authenticator),
            Reports(authenticator=authenticator),
            Segments(authenticator=authenticator),
            Unsubscribes(authenticator=authenticator, campaign_id=campaign_id),
        ]
