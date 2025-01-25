#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Iterator, List, Mapping, Optional

import dpath
from airbyte_protocol_dataclasses.models import AirbyteConnectionStatus, AirbyteMessage, AirbyteStateMessage

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.
WARNING: Do not modify this file.
"""


# Declarative Source
class SourceGoogleSheets(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})
