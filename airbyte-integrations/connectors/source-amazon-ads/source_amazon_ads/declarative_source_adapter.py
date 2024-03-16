#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from logging import Logger
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.models import AirbyteConnectionStatus
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import ConnectorSpecification


class DeclarativeSourceAdapter(YamlDeclarativeSource):
    def __init__(self, source: AbstractSource) -> None:
        self._source = source
        super().__init__(path_to_yaml="manifest.yaml")
        self._set_adapted_methods()

    @property
    def name(self) -> str:
        return self._source.name

    def spec(self, logger: Logger) -> ConnectorSpecification:
        return self._source.spec(logger)

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        self._source.profiles_stream = self._get_profiles_stream(config)
        return self._source.check(logger, config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        all_streams = self._source.streams(config, self._get_profiles_stream(config))
        return all_streams

    def _validate_source(self) -> None:
        """Skipping manifest validation as it can be incomplete when use adapter"""
        return

    def _set_adapted_methods(self) -> None:
        """
        Since the adapter is intended to smoothly migrate the connector,
        this method determines whether each of methods `spec`, `check`, and `streams` was declared in the manifest file
        and if yes, makes the source use it, otherwise the method defined in the source will be used
        """
        adapted_methods = ("spec",)
        for method in adapted_methods:
            if method in self.resolved_manifest:
                self._source.__setattr__(method, getattr(super(), method))

    def _get_profiles_stream(self, config):
        declarative_streams = super().streams(config)
        return [stream for stream in declarative_streams if stream.name == "profiles"][0]
