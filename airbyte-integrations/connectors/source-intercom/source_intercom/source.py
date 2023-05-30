#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Iterator, List, Mapping, MutableMapping, Union

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceIntercom(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        self._debug = True
        yield from super().read(logger, config, catalog, state)
