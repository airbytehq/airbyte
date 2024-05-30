#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import Contacts


# Hybrid Declarative Source
class SourceSendgrid(YamlDeclarativeSource):
    def __init__(self):
        # this takes care of check and other methods
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # get all the lowcode streams
        streams = super().streams(config)
        authenticator = TokenAuthenticator(config["api_key"])
        # this stream download a csv file from sendgrid and emits the records
        # it's not currently easy to do in lowcode, so we do it in python
        streams.append(Contacts(authenticator=authenticator))
        return streams
