#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from base_python import BaseSource
from base_python.logger import AirbyteLogger
from airbyte_protocol import AirbyteCatalog
from .client import Client
from typing import Mapping, Any
from .api import CallsStream


class SourceZendeskTalk(BaseSource):
    client_class = Client

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Catalog info of base python version doesn't include a part of necessary data for tests.
             This should be fixed after migration to CDK version"""
        catalog = super().discover(logger=logger, config=config)
        for stream in catalog.streams:
            if stream.name in ['calls', "call_legs"]:
                stream.source_defined_cursor = True
                stream.default_cursor_field = [CallsStream.cursor_field]
                # stream.source_defined_primary_key = ["id"]
        return catalog
