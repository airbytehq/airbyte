#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Iterable, List

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.yaml_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.streams.http import HttpStream


class LowCodeSourceAdapter:
    def __init__(self, manifest: Dict[str, Any]):
        # Request and response messages are only emitted for a sources that have debug turned on
        self._source = ManifestDeclarativeSource(manifest, debug=True)

    def get_http_streams(self, config: Dict[str, Any]) -> List[HttpStream]:
        return [
            stream.retriever
            for stream in self._source.streams(config=config)
            if isinstance(stream, DeclarativeStream) and isinstance(stream.retriever, HttpStream)
        ]

    def read_stream(self, stream: str, config: Dict[str, Any]) -> Iterable[AirbyteMessage]:
        configured_catalog = ConfiguredAirbyteCatalog.parse_obj(
            {
                "streams": [
                    {
                        "stream": {
                            "name": stream,
                            "json_schema": {},
                            "supported_sync_modes": ["full_refresh", "incremental"],
                        },
                        "sync_mode": "full_refresh",
                        "destination_sync_mode": "overwrite",
                    }
                ]
            }
        )
        generator = self._source.read(logger=self._source.logger, config=config, catalog=configured_catalog)
        for message in generator:
            yield message
