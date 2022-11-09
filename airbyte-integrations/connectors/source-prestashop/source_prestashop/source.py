#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""

import logging
from typing import Any, Iterator, List, Mapping, MutableMapping, Union

from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


# Declarative Source
class SourcePrestashop(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "prestashop.yaml"})

    def _validate_and_transform(self, config: Mapping[str, Any]):
        if not config.get("_allow_http"):
            if not config["url"].lower().startswith("https://"):
                raise Exception(f"Invalid url: {config['url']}, only https scheme is allowed")
        return config

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        config = self._validate_and_transform(config)
        return super().discover(logger, config)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        config = self._validate_and_transform(config)
        return super().check(logger, config)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        config = self._validate_and_transform(config)
        return super().read(logger, config, catalog, state)
