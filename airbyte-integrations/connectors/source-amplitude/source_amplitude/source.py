#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from base64 import b64encode
from typing import Any, List, Mapping, Optional

from source_amplitude.streams import Events

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceAmplitude(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    # def __init__(self):
    #     super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def _convert_auth_to_token(self, username: str, password: str) -> str:
        username = username.encode("latin1")
        password = password.encode("latin1")
        token = b64encode(b":".join((username, password))).strip().decode("ascii")
        return token

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = super().streams(config=config)
        auth = TokenAuthenticator(token=self._convert_auth_to_token(config["api_key"], config["secret_key"]), auth_method="Basic")
        streams.append(
            Events(
                authenticator=auth,
                start_date=config["start_date"],
                data_region=config.get("data_region", "Standard Server"),
                event_time_interval={"size_unit": "hours", "size": config.get("request_time_range", 24)},
            )
        )
        return streams
