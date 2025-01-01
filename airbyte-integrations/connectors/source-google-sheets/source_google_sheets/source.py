#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
import dpath
from typing import Any, Mapping, Optional, List, Iterator

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_protocol_dataclasses.models import AirbyteConnectionStatus, AirbyteStateMessage, AirbyteMessage

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
        manifest_definitions = self.resolved_manifest["definitions"]
        dynamic_stream = self.resolved_manifest["dynamic_streams"][0]
        retriever_response_filters_path = ["retriever", "requester", "error_handler", "error_handlers", 0, "response_filters"]

        component_resolver_filters_for_check_operation = dpath.get(manifest_definitions, ["response_filters", "check_operation_single_sheet_response_error_filters"], None)
        components_resolver_requester_filters_path = ["components_resolver"] + retriever_response_filters_path
        dpath.set(dynamic_stream, components_resolver_requester_filters_path, value=component_resolver_filters_for_check_operation)

        return super().check(logger, config)
