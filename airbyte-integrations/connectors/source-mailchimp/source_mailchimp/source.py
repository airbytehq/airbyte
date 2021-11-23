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

from .streams import Campaigns, EmailActivity, Lists


class HttpBasicAuthenticator(TokenAuthenticator):
    def __init__(self, auth: Tuple[str, str], auth_method: str = "Basic", **kwargs):
        # API keys have the format <key>-<data_center>.
        # See https://mailchimp.com/developer/marketing/docs/fundamentals/#api-structure
        self.data_center = auth[1].split("-").pop()
        auth_string = f"{auth[0]}:{auth[1]}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        super().__init__(token=b64_encoded, auth_method=auth_method, **kwargs)


class SourceMailchimp(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            client = MailChimp(mc_api=config["apikey"], mc_user=config["username"])
            client.ping.get()
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = HttpBasicAuthenticator(auth=("anystring", config["apikey"]))
        streams_ = [Lists(authenticator=authenticator), Campaigns(authenticator=authenticator), EmailActivity(authenticator=authenticator)]

        return streams_
