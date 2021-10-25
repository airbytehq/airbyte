#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

from airbyte_protocol import AirbyteCatalog
from base_python import BaseSource
from base_python.logger import AirbyteLogger

from .api import CallsStream
from .client import Client


class SourceZendeskTalk(BaseSource):
    client_class = Client

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Catalog info of base python version doesn't include a part of necessary data for tests.
        This should be fixed after migration to CDK version"""
        catalog = super().discover(logger=logger, config=config)
        for stream in catalog.streams:
            # now 2 below streams supports incremental logic
            if stream.name in ["calls", "call_legs"]:
                stream.source_defined_cursor = True
                stream.default_cursor_field = [CallsStream.cursor_field]
        return catalog
