#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from logging import Logger
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import AirbyteConnectionStatus
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_protocol.models import AirbyteCatalog, AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog


class DeclarativeSourceAdapter(YamlDeclarativeSource):
    def __init__(self, source: AbstractSource) -> None:
        super().__init__(path_to_yaml="manifest.yaml")
        self._source = source

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        return self._source.check(logger, config)

    def discover(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        return self._source.discover(logger, config)

    def read(
        self,
        logger: Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:
        return self._source.read(logger, config, catalog, state)

    # def _validate_source(self) -> None:
    #     # TODO ???
    #     return
