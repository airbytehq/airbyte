#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Iterator, List

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, ConfiguredAirbyteCatalog, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.yaml_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.streams.http import HttpStream
from connector_builder.impl.adapter import CdkAdapter, CdkAdapterFactory


class LowCodeSourceAdapter(CdkAdapter):
    def __init__(self, manifest: Dict[str, Any], limit_page_fetched_per_slice, limit_slices_fetched):
        # Request and response messages are only emitted for a sources that have debug turned on
        self._source = ManifestDeclarativeSource(
            manifest,
            debug=True,
            component_factory=ModelToComponentFactory(limit_page_fetched_per_slice, limit_slices_fetched)
        )

    def get_http_streams(self, config: Dict[str, Any]) -> List[HttpStream]:
        http_streams = []
        for stream in self._source.streams(config=config):
            if isinstance(stream, DeclarativeStream):
                if isinstance(stream.retriever, HttpStream):
                    http_streams.append(stream.retriever)
                else:
                    raise TypeError(
                        f"A declarative stream should only have a retriever of type HttpStream, but received: {stream.retriever.__class__}"
                    )
            else:
                raise TypeError(
                    f"A declarative source should only contain streams of type DeclarativeStream, but received: {stream.__class__}"
                )
        return http_streams

    def read_stream(self, stream: str, config: Dict[str, Any]) -> Iterator[AirbyteMessage]:
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

        # the generator can raise an exception
        # iterate over the generated messages. if next raise an exception, catch it and yield it as an AirbyteLogMessage
        try:
            yield from generator
        except Exception as e:
            yield AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=str(e)))
            return


class LowCodeSourceAdapterFactory(CdkAdapterFactory):

    def __init__(self, max_pages_per_slice, max_slices):
        self._max_pages_per_slice = max_pages_per_slice
        self._max_slices = max_slices

    def create(self, manifest: Dict[str, Any]) -> CdkAdapter:
        return LowCodeSourceAdapter(manifest, self._max_pages_per_slice, self._max_slices)
