#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from source_notion.streams import Blocks, Pages
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class SourceNotion(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def _get_authenticator(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        credentials = config.get("credentials", {})
        auth_type = credentials.get("auth_type")
        token = credentials.get("access_token") if auth_type == "OAuth2.0" else credentials.get("token")

        if credentials and token:
            return TokenAuthenticator(token)

        # The original implementation did not support OAuth, and therefore had no "credentials" key.
        # We can maintain backwards compatibility for OG connections by checking for the deprecated "access_token" key, just in case.
        if config.get("access_token"):
            return TokenAuthenticator(config["access_token"])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = super().streams(config)

        authenticator = self._get_authenticator(config)
        args = {"authenticator": authenticator, "config": config}

        blocks_parent = Pages(**args)
        blocks_stream = Blocks(parent=blocks_parent, **args)

        streams.append(blocks_stream)
        return streams
