#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import pendulum
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_slack.streams import Threads


class SourceSlack(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def _threads_authenticator(self, config: Mapping[str, Any]):
        # Added to maintain backward compatibility with previous versions
        if "api_token" in config:
            return TokenAuthenticator(config["api_token"])

        credentials = config.get("credentials", {})
        credentials_title = credentials.get("option_title")
        if credentials_title == "Default OAuth2.0 authorization":
            return TokenAuthenticator(credentials["access_token"])
        elif credentials_title == "API Token Credentials":
            return TokenAuthenticator(credentials["api_token"])
        else:
            raise Exception(f"No supported option_title: {credentials_title} specified. See spec.json for references")

    def get_threads_stream(self, config: Mapping[str, Any]) -> HttpStream:
        authenticator = self._threads_authenticator(config)
        default_start_date = pendulum.parse(config["start_date"])
        # this field is not exposed to spec, used only for testing purposes
        end_date = config.get("end_date")
        end_date = end_date and pendulum.parse(end_date)
        threads_lookback_window = pendulum.Duration(days=config["lookback_window"])
        channel_filter = config.get("channel_filter", [])
        include_private_channels = config.get("include_private_channels", False)
        threads = Threads(
            authenticator=authenticator,
            default_start_date=default_start_date,
            end_date=end_date,
            lookback_window=threads_lookback_window,
            channel_filter=channel_filter,
            include_private_channels=include_private_channels,
        )
        return threads

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        declarative_streams = super().streams(config)

        threads_stream = self.get_threads_stream(config)
        declarative_streams.append(threads_stream)

        return declarative_streams
