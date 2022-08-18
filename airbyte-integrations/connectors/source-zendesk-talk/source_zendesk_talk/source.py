#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import base64
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from requests.auth import HTTPBasicAuth

from source_zendesk_talk.streams import (
    AccountOverview,
    Addresses,
    AgentsActivity,
    AgentsOverview,
    CallLegs,
    Calls,
    CurrentQueueActivity,
    GreetingCategories,
    Greetings,
    IVRMenus,
    IVRRoutes,
    IVRs,
    PhoneNumbers,
)


class BasicApiTokenAuthenticator(TokenAuthenticator):
    """basic Authorization header"""

    def __init__(self, email: str, password: str):
        # for API token auth we need to add the suffix '/token' in the end of email value
        email_login = email + "/token"
        token = base64.b64encode(f"{email_login}:{password}".encode("utf-8"))
        super().__init__(token.decode("utf-8"), auth_method="Basic")


class SourceZendeskTalk(AbstractSource):
    @classmethod
    def get_authenticator(cls, config: Mapping[str, Any]) -> requests.auth.AuthBase:
        # old authentication flow support
        if "access_token" in config and "email" in config:
            return HTTPBasicAuth(username=f'{config["email"]}/token', password=config["access_token"])
        # new authentication flow
        auth = config["credentials"]
        if auth:
            if auth["credentials"] == "oauth2.0":
                return TokenAuthenticator(token=auth["access_token"])
            elif auth["credentials"] == "api_token":
                return HTTPBasicAuth(username=f'{auth["email"]}/token', password=auth["api_token"])
            else:
                raise Exception(f"Not implemented authorization method: {auth['credentials']}")

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        authenticator = self.get_authenticator(config)
        stream = AccountOverview(authenticator=authenticator, subdomain=config["subdomain"])

        account_info = next(iter(stream.read_records(sync_mode=SyncMode.full_refresh)), None)
        if not account_info:
            raise RuntimeError("Unable to read account information, please check the permissions of your token")

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)
        common_kwargs = dict(authenticator=authenticator, subdomain=config["subdomain"])
        incremental_kwargs = dict(**common_kwargs, start_date=pendulum.parse(config["start_date"]))

        return [
            AccountOverview(**common_kwargs),
            Addresses(**common_kwargs),
            AgentsActivity(**common_kwargs),
            AgentsOverview(**common_kwargs),
            Calls(**incremental_kwargs),
            CallLegs(**incremental_kwargs),
            CurrentQueueActivity(**common_kwargs),
            Greetings(**common_kwargs),
            GreetingCategories(**common_kwargs),
            IVRMenus(**common_kwargs),
            IVRRoutes(**common_kwargs),
            IVRs(**common_kwargs),
            PhoneNumbers(**common_kwargs),
        ]
