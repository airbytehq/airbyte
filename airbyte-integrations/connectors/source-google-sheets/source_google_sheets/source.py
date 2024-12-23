#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Mapping, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_protocol_dataclasses.models import AirbyteConnectionStatus

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.
WARNING: Do not modify this file.
"""


# Declarative Source
class SourceGoogleSheets(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        resolver_filters = self.resolved_manifest["dynamic_streams"][0]["components_resolver"]["retriever"]["requester"]["error_handler"][
            "error_handlers"
        ][0]["response_filters"]
        filters_for_check_operation = self.resolved_manifest["definitions"]["response_filters"]["check_operation_resolver_filters"]
        resolver_filters.clear()
        resolver_filters.extend(filters_for_check_operation)
        return super().check(logger, config)
