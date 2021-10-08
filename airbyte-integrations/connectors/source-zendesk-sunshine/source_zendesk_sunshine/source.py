#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import base64
from typing import Any, List, Mapping, Tuple

import pendulum
import requests

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, HttpAuthenticator

from .common import get_base_api_url, get_base_url

from .streams import Limits, ObjectRecords, ObjectTypePolicies, ObjectTypes, RelationshipRecords, RelationshipTypes


class OauthAuthenticator(HttpAuthenticator):
    def __init__(self, config: Mapping[str, str], **kwargs):
        self.auth_method = "Bearer"
        self.auth_header = "Authorization"
        self.access_token = config.get("access_token")
        self.base_url = get_base_url(subdomain=config["subdomain"])
        self.redirect_uri = "http://localhost"
        super().__init__(**kwargs)

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self.auth_method} {self.access_token}"}


class Base64HttpAuthenticator(TokenAuthenticator):
    def __init__(self, auth: Tuple[str, str], auth_method: str = "Basic", **kwargs):
        auth_string = f"{auth[0]}:{auth[1]}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        super().__init__(token=b64_encoded, auth_method=auth_method, **kwargs)


class SourceZendeskSunshine(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            pendulum.parse(config["start_date"], strict=True)
            authenticator = self.get_authenticator(config)
            stream = Limits(authenticator=authenticator, subdomain=config["subdomain"],
                            start_date=pendulum.parse(config["start_date"]))
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as e:
            return False, repr(e)

    def get_authenticator(self, config):
        if auth := config.get("authentication"):
            if api_token := auth.get("api_token"):
                authenticator = Base64HttpAuthenticator(auth=(f'{config["email"]}/token', api_token))
            elif oauth_credentials := auth.get("oauth_credentials"):
                authorization_code = oauth_credentials["authorization_code"]
                client_id = oauth_credentials["client_id"]
                client_secret = oauth_credentials["client_secret"]
                authenticator = OauthAuthenticator(config)

        else:
            # Legacy spec support for backward compatibility
            authenticator = Base64HttpAuthenticator(auth=(f'{config["email"]}/token', config["api_token"]))
        return authenticator

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        CustomObjectEvents stream is an early access stream. (looks like it is a new feature)
        It requires activation in site ui + manual activation from Zendesk via call.
        I requested the call, but since they did not approve it,
        this endpoint will return 403 Forbidden. Thats why it is disabled here.

        Jobs stream is also commented out. Reason: It is dynamic.
        It can have the data, but this data have time to live.
        After this time is passed we have no data. It will require permanent population, to pass
        the test criteria `stream should contain at least 1 record)
        """
        authenticator = self.get_authenticator(config)
        args = {"authenticator": authenticator, "subdomain": config["subdomain"], "start_date": config["start_date"]}
        return [
            ObjectTypes(**args),
            ObjectRecords(**args),
            RelationshipTypes(**args),
            RelationshipRecords(**args),
            # CustomObjectEvents(**args),
            ObjectTypePolicies(**args),
            # Jobs(**args),
            Limits(**args),
        ]
