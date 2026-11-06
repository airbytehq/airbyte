#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceOkta(YamlDeclarativeSource):
    def __init__(
        self,
        catalog: Optional[ConfiguredAirbyteCatalog] = None,
        config: Optional[Mapping[str, Any]] = None,
        state: Optional[List[AirbyteStateMessage]] = None,
        **kwargs: Any,
    ):
        super().__init__(path_to_yaml="manifest.yaml", catalog=catalog, config=config, state=state)
