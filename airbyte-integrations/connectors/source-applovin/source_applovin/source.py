#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator, Mapping, Any, List, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source, AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_applovin.streams import Campaigns, Creatives, Targets


class SourceApplovin(AbstractSource):

    base_url = f"https://oauth.applovin.com/oauth/v1/"
    def get_access_token(self, config) -> Tuple[any, any]:
        body = {
            "grant_type": "client_credentials",
            "scope" : "campaigns:read creatives:read",
            "client_id" : config["client_id"],
            "client_secret" : config["client_secret"]
        }

        url = f"https://oauth.applovin.com/oauth/v1/access_token"

        try:
            response = requests.post(url, data=body)
            response.raise_for_status()
            json_response = response.json()
            return json_response.get("accessToken", {}).get("access_token", None), None
        except requests.exceptions.RequestException as e:
            return None, e

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        access_token = self.get_access_token(config)
        token_value = access_token[0]
        token_exception = access_token[1]

        if token_exception:
            return False, token_exception

        if token_value:
            auth = TokenAuthenticator(token=token_value).get_auth_header()
            try:
                response = requests.get(f"https://o.applovin.com/campaign_management/v1/campaigns", headers=auth)
                response.raise_for_status()
                return True, None
            except requests.exceptions.RequestException as e:
                return False, e
        return False, "Token not found"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        access_token = self.get_access_token(config)
        auth = TokenAuthenticator(token=access_token[0])

        args = {
            "authenticator": auth
        }
        return [Campaigns(**args), Creatives(**args), Targets(**args)]


