#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_notion.streams import Blocks, Pages


class SourceNotion(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def _get_authenticator(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        """
        Creates and returns the appropriate authenticator for the Blocks stream.
        Supports legacy auth format as well as current token/oauth implementations.
        """
        credentials = config.get("credentials", {})
        auth_type = credentials.get("auth_type")
        token = credentials.get("access_token") if auth_type == "OAuth2.0" else credentials.get("token")

        if credentials and token:
            return TokenAuthenticator(token)

        # The original implementation did not support multiple auth methods, and therefore had no "credentials" key.
        if config.get("access_token"):
            return TokenAuthenticator(config["access_token"])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Overrides the declarative streams method to instantiate and append the Python Blocks stream
        to the list of declarative streams.
        """
        streams = super().streams(config)

        authenticator = self._get_authenticator(config)
        args = {"authenticator": authenticator, "config": config}

        # Blocks stream is a substream of Pages, so we also need to instantiate the parent stream.
        blocks_parent = Pages(**args)
        blocks_stream = Blocks(parent=blocks_parent, **args)

        streams.append(blocks_stream)
        return streams
