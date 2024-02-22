#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from logging import Logger
from typing import Any, List, Mapping

from airbyte_cdk.models import AirbyteConnectionStatus
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import ConnectorSpecification


class DeclarativeSourceAdapter(YamlDeclarativeSource):
    def __init__(self, source: AbstractSource) -> None:
        super().__init__(path_to_yaml="manifest.yaml")
        self._source = source
        self._set_adapted_methods()

    def spec(self, logger: Logger) -> ConnectorSpecification:
        return self._source.spec(logger)

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        return self._source.check(logger, config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._source.streams(config)

    def _validate_source(self) -> None:
        """Skipping manifest validation as it can be incomplete when use adapter"""
        return

    def _set_adapted_methods(self) -> None:
        adapted_methods = ("spec", "check", "streams")
        for method in adapted_methods:
            if method in self.resolved_manifest:
                self._source.__setattr__(method, getattr(super(), method))
