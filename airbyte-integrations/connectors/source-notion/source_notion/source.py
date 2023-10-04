#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import Blocks, Databases, Pages, Users


class NotionAuthenticator:
    def __init__(self, config: Mapping[str, Any]):
        self.config = config

    def get_access_token(self):
        credentials = self.config.get("credentials")
        if credentials:
            auth_type = credentials.get("auth_type")
            if auth_type == "OAuth2.0":
                return TokenAuthenticator(credentials.get("access_token"))
            return TokenAuthenticator(credentials.get("token"))

        # support the old config
        if "access_token" in self.config:
            return TokenAuthenticator(self.config.get("access_token"))


class SourceNotion(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            authenticator = NotionAuthenticator(config).get_access_token()
            stream = Users(authenticator=authenticator, config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            # The most likely user error will be incorrectly configured credentials. We can provide a specific error message for those cases. Otherwise, the stock Notion API message should suffice.
            error_code = e.response.json().get("code")
            if error_code == "unauthorized":
                return (
                    False,
                    "The provided API access token is invalid. Please double-check that you input the correct token and have granted the necessary permissions to your Notion integration.",
                )
            if error_code == "restricted_resource":
                return (
                    False,
                    "The provided API access token does not have the correct permissions configured. Please double-check that you have granted all the necessary permissions to your Notion integration.",
                )
            return (
                False,
                f"{e.response.json().get('message', 'An unexpected error occured while connecting to Notion. Please check your credentials and try again.')}",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}")
        authenticator = NotionAuthenticator(config).get_access_token()
        args = {"authenticator": authenticator, "config": config}
        pages = Pages(**args)
        blocks = Blocks(parent=pages, **args)

        return [Users(**args), Databases(**args), pages, blocks]
