#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.abstract_stream_facade import AbstractStreamFacade


class ConcurrentSourceAdapter(AbstractSource, ABC):
    def __init__(self, concurrent_source: ConcurrentSource, **kwargs: Any) -> None:
        """
        ConcurrentSourceAdapter is a Source that wraps a concurrent source and exposes it as a regular source.

        The source's streams are still defined through the streams() method.
        Streams wrapped in a StreamFacade will be processed concurrently.
        Other streams will be processed sequentially as a later step.
        """
        self._concurrent_source = concurrent_source
        super().__init__(**kwargs)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:
        abstract_streams = self._select_abstract_streams(config, catalog)
        concurrent_stream_names = {stream.name for stream in abstract_streams}
        configured_catalog_for_regular_streams = ConfiguredAirbyteCatalog(
            streams=[stream for stream in catalog.streams if stream.stream.name not in concurrent_stream_names]
        )
        if abstract_streams:
            yield from self._concurrent_source.read(abstract_streams)
        if configured_catalog_for_regular_streams.streams:
            yield from super().read(logger, config, configured_catalog_for_regular_streams, state)

    def _select_abstract_streams(self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog) -> List[AbstractStream]:
        """
        Selects streams that can be processed concurrently and returns their abstract representations.
        """
        all_streams = self.streams(config)
        stream_name_to_instance: Mapping[str, Stream] = {s.name: s for s in all_streams}
        abstract_streams: List[AbstractStream] = []
        for configured_stream in configured_catalog.streams:
            stream_instance = stream_name_to_instance.get(configured_stream.stream.name)
            if not stream_instance:
                if not self.raise_exception_on_missing_stream:
                    continue
                raise KeyError(
                    f"The stream {configured_stream.stream.name} no longer exists in the configuration. "
                    f"Refresh the schema in replication settings and remove this stream from future sync attempts."
                )
            if isinstance(stream_instance, AbstractStreamFacade):
                abstract_streams.append(stream_instance.get_underlying_stream())
        return abstract_streams
