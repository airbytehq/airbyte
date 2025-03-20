#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping, Optional

from airbyte_cdk import TState
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.
WARNING: Do not modify this file.
"""


# Declarative Source
class SourceGreenhouse(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})
